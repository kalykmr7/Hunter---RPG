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
        "🗺 SISTEMA DE VIAGEM\n\n"
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
    
async def exibir_mapa(update, context, mapa_id):
    user_id = update.effective_user.id 
    query = getattr(update, "callback_query", None)
    
    print(f"DEBUG VIAGEM: Entrando em exibir_mapa. ID: {mapa_id}")
    
    database.curar_personagem_total(user_id)
    database.atualizar_mapa_personagem(user_id, mapa_id)
    jogador = database.get_jogador(user_id)

    if not jogador:
        return

    mapa_info = next((m for m in lista_mapas if m["id"] == mapa_id), None)
    if not mapa_info:
        return

    nome_mapa = mapa_info.get('nome', 'Área Desconhecida')
    imagem_nome = mapa_info.get('imagem', 'capa.png')
    caminho_img = os.path.join("imagens", imagem_nome)

    keyboard = []
    
    if mapa_id == 0:
        texto = f"🏰 MENU PRINCIPAL\n\n👤 {jogador['nick']}\n📍 Localização: {nome_mapa}"
        keyboard.append([InlineKeyboardButton("🗺️ Viajar", callback_data="mapas")])
        keyboard.append([InlineKeyboardButton("📊 Status", callback_data="status")])
        keyboard.append([InlineKeyboardButton("🎁 Login Diário", callback_data="login_diario")])
        # Correção aqui: Acesso via ['coluna'] em vez de .get('coluna')
        if jogador['pet_nome']:
            keyboard.append([InlineKeyboardButton("🐾 Pet", callback_data="pet")])
            
    else:
        texto = f"📍 {mapa_info.get('descricao', 'Um lugar aparentemente tranquilo e seguro...')}"
        keyboard.append([InlineKeyboardButton("⚔️ Caçar", callback_data=f"procurar_{mapa_id}")])
        keyboard.append([InlineKeyboardButton("🗺️ Viajar", callback_data="mapas")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        with open(caminho_img, "rb") as foto:
            if query:
                await query.answer()
                await query.edit_message_media(media=InputMediaPhoto(media=foto, caption=texto), reply_markup=reply_markup)
            else:
                await update.message.reply_photo(photo=foto, caption=texto, reply_markup=reply_markup)
    except FileNotFoundError:
        if query:
            await query.edit_message_caption(caption=texto, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text=texto, reply_markup=reply_markup)
            
        
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