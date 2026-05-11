# handlers/mochila.py

import os
import database
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

async def ver_mochila(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    pagina = int(query.data.split("_")[1]) if "_" in query.data and query.data.split("_")[1].isdigit() else 0

    itens_brutos = database.get_inventario(user_id) 
    jogador = database.get_jogador(user_id)
    
    # BUSCA A LISTA MESTRE PARA FILTRAR O SUBTIPO 'ovo'
    conn = database.conectar()
    # Criamos um set de nomes que são ovos para filtrar rápido
    cursor = conn.execute("SELECT nome FROM itens_mestre WHERE subtipo = 'ovo'")
    nomes_ovos = {r['nome'] for r in cursor.fetchall()}
    conn.close()

    # FILTRAGEM: Remove ovos da visualização da mochila
    equipamentos = [i for i in itens_brutos if i['tipo'] == 'equipamento']
    outros_itens = [i for i in itens_brutos if i['tipo'] != 'equipamento' and i['item_nome'] not in nomes_ovos]
    
    itens_por_pagina = 10
    inicio = pagina * itens_por_pagina
    fim = inicio + itens_por_pagina
    equip_pagina = equipamentos[inicio:fim]

    texto = f"🎒 Mochila\nSlots: {len(equipamentos)}/{jogador['mochila_slots']}\n\n"
    keyboard = []
    if equip_pagina:
        for item in equip_pagina:
            refino = f" (+{item['nivel_refino']})" if item['nivel_refino'] > 0 else ""
            status = "✅ " if item['equipado'] == 1 else ""
            keyboard.append([InlineKeyboardButton(f"{status}{item['item_nome']}{refino}", callback_data=f"item_ver_{item['id']}")])
    
    if outros_itens and pagina == 0:
        texto += "📦 Itens e Materiais:\n"
        for i in outros_itens:
            texto += f"• {i['item_nome']} (x{i['quantidade']})\n"

    nav = []
    if pagina > 0: nav.append(InlineKeyboardButton("⬅️", callback_data=f"mochila_{pagina-1}"))
    if fim < len(equipamentos): nav.append(InlineKeyboardButton("➡️", callback_data=f"mochila_{pagina+1}"))
    if nav: keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("⬅️ Voltar", callback_data="status")])
    await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def detalhes_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe os detalhes de um item específico selecionado na mochila."""
    query = update.callback_query
    await query.answer()
    
    item_id = query.data.replace("item_ver_", "")
    
    conn = database.conectar()
    # Buscamos o item específico pelo ID único na mochila
    item_inv = conn.execute("SELECT * FROM inventario WHERE id = ?", (item_id,)).fetchone()
    # Buscamos as propriedades desse item na tabela mestre
    item_mestre = conn.execute("SELECT * FROM itens_mestre WHERE nome = ?", (item_inv['item_nome'],)).fetchone()
    conn.close()

    if not item_inv:
        await query.answer("Item não encontrado.")
        return

    # Cálculo do bônus real incluindo o refino (+2 por nível)
    poder_extra = (item_inv['nivel_refino'] or 0) * 2 
    total_bonus = item_mestre['valor_efeito'] + poder_extra
    
    refino_titulo = f" +{item_inv['nivel_refino']}" if item_inv['nivel_refino'] > 0 else ""

    texto = (
        f"🔍 {item_mestre['nome']}{refino_titulo}\n"
        f"_{item_mestre['descricao']}_\n\n"
        f"📊 Bônus Total: +{total_bonus}\n"
        f"✨ (Bônus base: {item_mestre['valor_efeito']} | Forja: +{poder_extra})\n"
    )

    label_acao = "❌ Desequipar" if item_inv['equipado'] == 1 else "⚔️ Equipar"
    
    keyboard = [
        [InlineKeyboardButton(label_acao, callback_data=f"item_acao_{item_id}")],
        [InlineKeyboardButton("⬅️ Voltar", callback_data="mochila")]
    ]
    await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def executar_acao_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a ação de equipar ou desequipar o item."""
    query = update.callback_query
    item_id = query.data.replace("item_acao_", "")
    user_id = query.from_user.id

    # Chama a função no banco de dados que faz a troca de equipamentos
    sucesso, mensagem = database.equipar_desequipar_db(user_id, item_id)
    
    await query.answer(mensagem, show_alert=True)
    
    # Após equipar/desequipar, voltamos para a visualização da mochila
    await ver_mochila(update, context)
