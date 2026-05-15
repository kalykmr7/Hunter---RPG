#Lógica das viagens

import os
import database
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from modelos.mapas import lista_mapas

async def mostrar_mapas(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    jogador = database.get_jogador(user_id) 
    
    if not jogador:
        return

    # Pegamos os dados usando os nomes das colunas (Row)
    lvl_atual = jogador['level']
    
    # Tentamos pegar a localização, com um fallback (valor padrão) para evitar erros
    try:
        local_id_no_banco = jogador['mapa_atual']
    except Exception:
        local_id_no_banco = 0 # Assume Lobby se a coluna falhar

    keyboard = []
    for mapa in lista_mapas:
        # Lógica Dinâmica de Ícones
        if mapa['id'] == local_id_no_banco:
            icone = "📍" # Você está aqui
            callback = "manter_local" 
        elif lvl_atual >= mapa['lvl_min']:
            icone = " " # Desbloqueado
            callback = f"ir_{mapa['id']}"
        else:
            icone = "🔒" # Bloqueado por nível
            callback = "mapa_bloqueado"
        
        keyboard.append([InlineKeyboardButton(
            f"{icone} {mapa['nome']} (Lvl {mapa['lvl_min']})", 
            callback_data=callback
        )])

    keyboard.append([InlineKeyboardButton("⬅ Voltar", callback_data="menu")])
    
    texto = (
        "🗺 Sistema de viajem\n\n"
        f"Lvl: ⭐ Lvl {lvl_atual}\n"
        "Selecione um destino abaixo:"
    )
    
    caminho_imagem = os.path.join("imagens", "capa.png")
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open(caminho_imagem, "rb") as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto, parse_mode="Markdown"),
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        await query.edit_message_caption(
            caption=texto + "\n\n⚠️ (capa.png não encontrada)", 
            reply_markup=reply_markup,
            parse_mode=None
        )

async def aviso_bloqueado(update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(
        "❌ Nível insuficiente! Continue caçando para liberar este mapa.", 
        show_alert=True
    )

async def manter_local(update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(
        "📍 Você já está neste local!", 
        show_alert=False
    )
    
# --- ARQUIVO: .\handlers\viagem.py ---

async def exibir_mapa(update, context, mapa_id):
    """Exibe a interface do mapa. Mapa 0 = Vila (Serviços), Mapa > 0 = Caça."""
    user_id = update.effective_user.id 
    query = getattr(update, "callback_query", None)
    
    # Garantimos que o ID seja um número inteiro para a comparação funcionar
    mapa_id = int(mapa_id)
    
    # 1. Atualizações de Estado
    database.curar_personagem_total(user_id)
    database.atualizar_mapa_personagem(user_id, mapa_id)
    
    jogador = database.get_jogador(user_id)
    if not jogador: return

    # 2. Busca informações do modelo do mapa
    mapa_info = next((m for m in lista_mapas if m["id"] == mapa_id), None)
    if not mapa_info: return

    caminho_img = os.path.join("imagens", mapa_info.get('imagem', 'capa.png'))
    keyboard = []

    # --- LÓGICA DE RAMIFICAÇÃO DA UI ---
    
    if mapa_id == 0:
        # INTERFACE DA VILA (Apenas aqui tem Ateliê e Login Diário)
        texto = (
            f"🏰 *{mapa_info['nome']}*\n"
            f"_{mapa_info['descricao']}_\n\n"
            f"👤 Caçador: {jogador['nick']}\n"
            f"💰 Gold: {jogador['gold']}\n"
            f"🐾 Pet: {jogador['pet_nome'] if jogador['pet_equipado'] else 'Nenhum'}"
        )
        keyboard.append([InlineKeyboardButton("🗺️ Viajar", callback_data="mapas")])
        keyboard.append([InlineKeyboardButton("🛠️ Ateliê", callback_data="atelie_menu")])
        keyboard.append([InlineKeyboardButton("🎁 Login Diário", callback_data="login_diario")])
    
    else:
        # INTERFACE DE CAÇA (Mapas 1 a 8)
        texto = (
            f"📍 {mapa_info['nome']}\n"
            f"_{mapa_info['descricao']}_\n\n"
            "O que deseja fazer nesta área?"
        )
        keyboard.append([InlineKeyboardButton("⚔️ Caçar", callback_data=f"procurar_{mapa_id}")])
        keyboard.append([InlineKeyboardButton("👹 Entrar na Masmorra", callback_data=f"entrar_masmorra_{mapa_id}")])
        keyboard.append([InlineKeyboardButton("🗺️ Viajar", callback_data="mapas")])

    # Botões utilitários (Aparecem em todos os mapas)
    botoes_utilitarios = [InlineKeyboardButton("📊 Status", callback_data="status")]
    if database.jogador_possui_pets(user_id):
        botoes_utilitarios.append(InlineKeyboardButton("🐾 Pet", callback_data="pet"))
    keyboard.append(botoes_utilitarios)

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if query:
            await query.answer()
            with open(caminho_img, "rb") as foto:
                await query.edit_message_media(
                    media=InputMediaPhoto(media=foto, caption=texto, parse_mode="Markdown"), 
                    reply_markup=reply_markup
                )
        else:
            with open(caminho_img, "rb") as foto:
                await update.message.reply_photo(photo=foto, caption=texto, reply_markup=reply_markup, parse_mode="Markdown")
    except FileNotFoundError:
        # Fallback caso a imagem falhe
        msg = f"{texto}\n\n⚠️ (Imagem não encontrada)"
        if query: await query.edit_message_caption(caption=msg, reply_markup=reply_markup, parse_mode="Markdown")
        else: await update.message.reply_text(text=msg, reply_markup=reply_markup, parse_mode="Markdown")            
            
        
async def entrar_no_mapa(update, context: ContextTypes.DEFAULT_TYPE):
    """Esta função apenas recebe o clique e chama a exibição"""
    query = update.callback_query
    
    # Extrai o ID do mapa do callback (ex: ir_1 -> 1)
    try:
        mapa_id = int(query.data.split("_")[1])
    except (IndexError, ValueError):
        await query.answer("❌ Erro ao identificar o mapa.")
        return

    # Chama a função que criamos no Passo 1
    await exibir_mapa(update, context, mapa_id)