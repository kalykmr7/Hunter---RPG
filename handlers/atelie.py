# --- ARQUIVO: .\handlers\atelie.py ---

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database

# Central de Receitas - Aqui você pode adicionar novos itens facilmente
RECEITAS = {
    "PocaoPequena": {
        "resultado": "Poção Pequena",
        "gold": 50,
        "ingredientes": [("Erva medicinal", 5)],
        "label": "🧪 Poção Pequena (5 Ervas)"
    },
    "PocaoMedia": {
        "resultado": "Poção Média",
        "gold": 100,
        "ingredientes": [("Erva medicinal", 3), ("Essência Mágica", 1)],
        "label": "⚗️ Poção Média (3 Erva + 1 Essência)"
    },
    "PocaoGrande": {
        "resultado": "Poção Grande",
        "gold": 200,
        "ingredientes": [("Erva medicinal", 5), ("Essência Mágica", 2)],
        "label": "🍯 Poção Grande (5 Erva + 2 Essência)"
    },
    "SuperFruta": {
        "resultado": "Super-Fruta",
        "gold": 300,
        "ingredientes": [("Fruta arco-íris", 10)],
        "label": "Super-Fruta (10 Fruta Arco-íris + 2 Essência) "
    }
}

async def menu_atelie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu principal do Ateliê"""
    query = update.callback_query
    await query.answer()
    
    texto = (
        "🛠️ Ateliê\n"
        "Bem-vindo ao ateliê! Aqui você pode aprimorar sua jornada.\n\n"
        "⚒️ Melhoria: Fortaleça seus equipamentos e acessórios.\n"
        "⚗️ Alquimia: Crie poções e elixires.\n"
        "💰 Venda: Desfaça-se do que não usa."
    )
    
    keyboard = [
        [InlineKeyboardButton("⚒️ Melhorar Itens", callback_data="atelie_forja_menu")],
        [InlineKeyboardButton("⚗️ Alquimia", callback_data="alquimia_menu")],
        [InlineKeyboardButton("💰 Vender Itens", callback_data="atelie_vender_lista_0")],
        [InlineKeyboardButton("⬅️ Voltar", callback_data="ir_0")]
    ]
    
    await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# --- SISTEMA DE VENDA ---

async def listar_venda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista itens para venda. Melhoria na detecção de página."""
    query = update.callback_query
    # Se a função for chamada sem um clique direto (via executar_venda), query já existe
    if not query: return
    
    user_id = query.from_user.id
    
    # LÓGICA DE PÁGINA ROBUSTA:
    # Se o final do query.data não for um número de página (ex: "lista_0"), assumimos 0.
    partes = query.data.split("_")
    ultima_parte = partes[-1]
    
    if ultima_parte.isdigit() and len(ultima_parte) < 4: # Se for um número pequeno, é página
        pagina = int(ultima_parte)
    else:
        pagina = 0 # Caso contrário (como ID de item), volta para o começo

    itens = database.get_inventario(user_id)
    # Filtro: Itens desequipados E que possuem preço maior que 0
    vendeis = [i for i in itens if i['equipado'] == 0]
    
    itens_per_page = 8
    inicio = pagina * itens_per_page
    fim = inicio + itens_per_page
    itens_pagina = vendeis[inicio:fim]

    # TEXTO COM STATUS DE OURO (Bom feedback visual para o jogador)
    jogador = database.get_jogador(user_id)
    texto = (
        f"💰 Loja do Ateliê (Pág {pagina + 1})\n"
        f"💳 Seu Ouro: `{jogador['gold']}g`\n\n"
        f"Selecione um item para ofertar:"
    )
    
    keyboard = []
    for item in itens_pagina:
        refino = f" (+{item['nivel_refino']})" if item['nivel_refino'] > 0 else ""
        keyboard.append([InlineKeyboardButton(f"📦 {item['item_nome']}{refino} x{item['quantidade']}", callback_data=f"vender_ver_{item['id']}")])

    nav = []
    if pagina > 0: nav.append(InlineKeyboardButton("⬅️", callback_data=f"atelie_vender_lista_{pagina-1}"))
    if fim < len(vendeis): nav.append(InlineKeyboardButton("➡️", callback_data=f"atelie_vender_lista_{pagina+1}"))
    if nav: keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("⬅️ Voltar", callback_data="atelie_menu")])
    
    await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    


async def vender_detalhes_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tela de confirmação com preço valorizado."""
    query = update.callback_query
    await query.answer()
    
    item_id = int(query.data.split("_")[-1])
    user_id = query.from_user.id
    
    conn = database.conectar()
    # Pega dados do inventário e do mestre ao mesmo tempo
    item = conn.execute("""
        SELECT i.id, i.item_nome, i.quantidade, i.nivel_refino, m.descricao, m.preco_gold 
        FROM inventario i JOIN itens_mestre m ON i.item_nome = m.nome WHERE i.id = ?
    """, (item_id,)).fetchone()
    conn.close()

    if not item: return

    # Cálculo do valor transparente para o jogador
    valor_unidade = int(item['preco_gold'] * 0.7) + (item['nivel_refino'] * 150)
    valor_total_stack = valor_unidade * item['quantidade']
    
    refino_txt = f"\n✨ Melhoria: +{item['nivel_refino']} (Bônus: +{item['nivel_refino']*150}g)" if item['nivel_refino'] > 0 else ""

    texto = (
        f"💰 Proposta de Compra\n\n"
        f"📦 Item: {item['item_nome']}\n"
        f"_{item['descricao']}_\n"
        f"📊 Quantidade: {item['quantidade']}{refino_txt}\n\n"
        f"💵 Oferta por unidade: `{valor_unidade} gold`\n"
        f"💰 Total pela pilha: `{valor_total_stack} gold`"
    )

    keyboard = [
        [InlineKeyboardButton(f"✅ Vender 1x ({valor_unidade}g)", callback_data=f"vender_exec_um_{item['id']}")],
    ]
    
    # Se tiver mais de 1, oferece opção de vender tudo
    if item['quantidade'] > 1:
        keyboard.append([InlineKeyboardButton(f"💰 Vender TODAS ({valor_total_stack}g)", callback_data=f"vender_exec_tudo_{item['id']}")])
        
    keyboard.append([InlineKeyboardButton("⬅️ Voltar", callback_data="atelie_vender_lista_0")])

    await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def executar_venda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executa a venda e garante a atualização visual."""
    query = update.callback_query
    user_id = query.from_user.id
    
    partes = query.data.split("_")
    tipo = partes[2]    # 'um' ou 'tudo'
    item_id = int(partes[3]) 
    
    vender_tudo = (tipo == "tudo")
    
    # 1. Faz a venda no banco
    sucesso, msg = database.vender_item_db(user_id, item_id, vender_tudo)
    
    if sucesso:
        # 2. Responde o popup
        await query.answer(msg, show_alert=False) # Mudamos para False (balão pequeno) para ser mais rápido
        database.atualizar_progresso_missao(user_id, 'venda', 1)
        
        # 3. ATUALIZAÇÃO VISUAL: Forçamos o reset da página
        query.data = "atelie_vender_lista_0"
        
        # Chamamos a função de lista para redesenhar a tela IMEDIATAMENTE
        await listar_venda(update, context)
    else:
        await query.answer(msg, show_alert=True)
    

# --- SISTEMA DE MELHORIA (EX-FORJA) ---

async def menu_forja(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista equipamentos equipados para melhoria"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    itens_equipados = database.get_todos_equipados(user_id)
    
    if not itens_equipados:
        await query.edit_message_caption(
            caption="❌ Você não está usando nenhum equipamento!\nEquipe algo na mochila para poder aplicar melhorias.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Voltar", callback_data="atelie_menu")]])
        )
        return

    texto = "⚒️ Melhoria\nQual item você deseja fortalecer hoje?"
    keyboard = []

    for item in itens_equipados:
        emoji = "⚔️" if item['subtipo'] == 'arma' else "🛡️"
        if item['subtipo'] == 'acessorio': emoji = " "
        
        label = f"{emoji} {item['item_nome']} (+{item['nivel_refino']})"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"forja_ver_{item['id']}")])

    keyboard.append([InlineKeyboardButton("⬅️ Voltar", callback_data="atelie_menu")])
    await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def detalhes_forja_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe custos de melhoria e bônus futuro"""
    query = update.callback_query
    await query.answer()
    
    item_id = int(query.data.split("_")[-1])
    
    conn = database.conectar()
    item = conn.execute("""
        SELECT i.id, i.item_nome, i.nivel_refino, m.valor_efeito, m.subtipo, m.nivel_max 
        FROM inventario i JOIN itens_mestre m ON i.item_nome = m.nome WHERE i.id = ?
    """, (item_id,)).fetchone()
    conn.close()

    if not item: return

    lvl_at = item['nivel_refino']
    if lvl_at >= item['nivel_max']:
        await query.edit_message_caption(caption=f"⭐ {item['item_nome']} já está no máximo!", 
                                         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Voltar", callback_data="atelie_forja_menu")]]))
        return

    # Lógica de Nome de Status
    if item['subtipo'] == 'arma': tipo_bonus = "ATQ"
    elif item['subtipo'] == 'armadura': tipo_bonus = "DEF"
    elif item['item_nome'] == 'Bússola': tipo_bonus = "SORTE"
    elif item['item_nome'] == 'Binóculos': tipo_bonus = "CRÍTICO"
    else: tipo_bonus = "PODER"

    prox = lvl_at + 1
    custo = 100 + (lvl_at * 200)
    v_at = item['valor_efeito'] + (lvl_at * 2)
    v_px = item['valor_efeito'] + (prox * 2)

    texto = (
        f"⚒️ Melhorando {item['item_nome']}\n"
        f"Nível: +{lvl_at} ➔ +{prox}\n"
        f"Status: {tipo_bonus} {v_at} ➔ {tipo_bonus} {v_px}\n"
        f"💰 Custo: {custo} Gold"
    )

    keyboard = [
        [InlineKeyboardButton(f"🔨 Melhorar (+{prox})", callback_data=f"executar_forja_{item['id']}_{custo}")],
        [InlineKeyboardButton("⬅️ Escolher Outro", callback_data="atelie_forja_menu")]
    ]
    await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard))

async def executar_forja(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a melhoria com animação de espera."""
    query = update.callback_query
    user_id = query.from_user.id
    
    # 1. Extrair dados
    dados = query.data.split("_")
    item_id = int(dados[2])
    custo = int(dados[3])
    
    # 2. Verificar se o jogador tem os requisitos antes de começar a "mágica"
    # Fazemos um check manual aqui ou confiamos no retorno da função do banco
    # Vou executar a lógica do banco primeiro. Se falhar, nem mostramos a animação.
    sucesso, msg = database.executar_refino_db(user_id, item_id, custo)
    
    if not sucesso:
        await query.answer(msg, show_alert=True)
        return

    # 3. FEEDBACK VISUAL INICIAL (Esconde botões e muda texto)
    await query.answer() # Fecha o loading do botão
    
    texto_processando = (
        "⚒️ Oficina de Melhoria\n\n"
        "✨ Aguarde enquanto a magia acontece... 6s"
    )
    
    # Editamos a mensagem removendo os botões (reply_markup=None)
    await query.edit_message_caption(
        caption=texto_processando, 
        reply_markup=None, 
        parse_mode="Markdown"
    )

    # 4. TEMPO DE ESPERA (6 segundos)
    await asyncio.sleep(6)

    # 5. RESULTADO FINAL
    database.atualizar_progresso_missao(user_id, 'forja', 1)
    
    # Busca dados atualizados do item
    item_atualizado = database.get_item_por_id_forja(item_id)
    nivel_novo = item_atualizado['nivel_refino']
    
    # Lógica de Nome de Status para o texto final
    if item_atualizado['subtipo'] == 'arma': tipo_bonus = "Atq"
    elif item_atualizado['subtipo'] == 'armadura': tipo_bonus = "Def"
    elif item_atualizado['item_nome'] == 'Bússola': tipo_bonus = "Sorte"
    else: tipo_bonus = "Contate o Admin."
    
    status_v = item_atualizado['valor_efeito'] + (nivel_novo * 2)

    texto_sucesso = (
        "✨ Melhoria completa!\n\n"
        f"✅ Seu {item_atualizado['item_nome']} subiu para +{nivel_novo}!\n"
        f"📊 Novo Status: {tipo_bonus} {status_v}\n\n"
        "O que deseja fazer agora?"
    )

    keyboard = [
        [InlineKeyboardButton(f"🔨 Melhorar (+{nivel_novo + 1})", callback_data=f"forja_ver_{item_id}")],
        [InlineKeyboardButton("⬅️ Voltar para Lista", callback_data="atelie_forja_menu")]
    ]

    await query.edit_message_caption(
        caption=texto_sucesso, 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="Markdown"
    )

# --- SISTEMA DE ALQUIMIA ---

async def menu_alquimia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o caldeirão de receitas"""
    query = update.callback_query
    await query.answer()
    
    texto = (
        "⚗️ Espaço para 'Faça voçê mesmo'\n"
        "Selecione uma receita abaixo:"
    )
    keyboard = []
    
    for rid, dados in RECEITAS.items():
        keyboard.append([InlineKeyboardButton(dados['label'], callback_data=f"exec_alquimia_{rid}")])
        
    keyboard.append([InlineKeyboardButton("⬅️ Voltar", callback_data="atelie_menu")])
    await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def executar_alquimia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lógica com animação de espera e consumo de Gold + Itens"""
    query = update.callback_query
    user_id = query.from_user.id
    receita_id = query.data.split("_")[-1]
    
    rec = RECEITAS.get(receita_id)
    if not rec: return

    # 1. Tenta consumir materiais e Gold no banco (Validação imediata)
    sucesso, msg = database.consumir_materiais_alquimia(user_id, rec['ingredientes'], rec['gold'])
    
    if not sucesso:
        await query.answer(msg, show_alert=True)
        return

    # 2. Inicia Animação de Espera
    await query.answer()
    texto_espera = (
        "⚗️ Executando alquimia...\n\n"
        "🧪 Os ingredientes estão sendo processados... 6s"
        
    )
    await query.edit_message_caption(caption=texto_espera, reply_markup=None, parse_mode="Markdown")

    # 3. Pausa Dramática (6 segundos)
    await asyncio.sleep(6)

    # 4. Entrega do Item
    from modelos.itens import buscar_dados_item
    item_final = buscar_dados_item(rec['resultado'])
    
    if item_final is None:
        await query.message.reply_text(f"⚠️ Erro Crítico: O item '{rec['resultado']}' não encontrado. Comunique o ADM.")
        return

    database.adicionar_item_inventario(user_id, item_final['nome'], item_final['tipo'], 1)

    # 5. Resultado Final
    texto_sucesso = (
        "✨ Criação realizada!\n\n"
        f"✅ Você criou: 1x {rec['resultado']}!\n"
        "O Ateliê está pronto para a próxima."
    )
    
    keyboard = [
        [InlineKeyboardButton("⚗️ Criar outro", callback_data="alquimia_menu")],
        [InlineKeyboardButton("⬅️ Voltar", callback_data="atelie_menu")]
    ]
    
    await query.edit_message_caption(caption=texto_sucesso, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")