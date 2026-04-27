# Comando /start e Menu principal

import os
import database
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from modelos.monstros import sortear_pet
from handlers.menu import menu_principal
from handlers import viagem

async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    
    database.resetar_localizacao(user_id)
    
    keyboard = [
        [
            InlineKeyboardButton("⚔️ Criar Conta", callback_data='registrar'),
            InlineKeyboardButton("Fazer Login", callback_data='login')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    texto = "Bem-vindo ao Reino de Hunter 🏰\nSua jornada começa agora."

    caminho_imagem = os.path.join("imagens", "capa.png")

    try:
        with open(caminho_imagem, "rb") as foto:
            await update.effective_chat.send_photo(
                photo=foto,
                caption=texto,
                reply_markup=reply_markup
            )

    except FileNotFoundError:
        await update.effective_chat.send_message(
            texto + "\n\n⚠️ (Imagem não encontrada)",
            reply_markup=reply_markup
        )

# 🥚 OVO
async def resgatar_presente(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    caminho_imagem = os.path.join('imagens', 'ovo.png')

    try:
        with open(caminho_imagem, 'rb') as foto:
            from telegram import InputMediaPhoto

            await query.edit_message_media(
                media=InputMediaPhoto(
                    media=foto,
                    caption="🎁 Você encontrou um ovo misterioso...\n\nClique para chocar!"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🥚 Chocar ovo", callback_data="chocar_ovo")]
                ])
            )

    except FileNotFoundError:
        await query.edit_message_caption(
            caption="🎁 Ovo misterioso...\n\nClique para chocar!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🥚 Chocar ovo", callback_data="chocar_ovo")]
            ])
        )


# 🐣 CHOCAR OVO
async def chocar_ovo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    pet = sortear_pet() 

    conn = database.conectar()
    cursor = conn.cursor()
    
    # Organizei o SQL para ficar fácil de ler: 7 campos = 7 interrogações
    cursor.execute("""
        UPDATE personagens 
        SET jogo_iniciado = 1, 
            pet_nome = ?, 
            pet_vida = ?, 
            pet_ataque = ?, 
            pet_defesa = ?, 
            pet_agilidade = ?, 
            pet_imagem = ?, 
            mapa_atual = 0
        WHERE user_id = ?
    """, (
        pet["nome"], 
        pet["vida"], 
        pet["ataque"], 
        pet["defesa"], 
        pet["agilidade"], 
        pet["imagem"], 
        user_id
    ))
    conn.commit()
    conn.close()

    caminho_foto_pet = os.path.join('imagens', pet["imagem"])
    
    texto_sucesso = (
        f"🎉 O OVO CHOCOU!\n\n"
        f"🐾 Seu novo companheiro: {pet['nome']}\n"
        f"⚔️ Status: Atk {pet['ataque']} | Def {pet['defesa']}\n\n"
        f"Agora você pode explorar o universo de Hunter!"
    )

    keyboard = [[InlineKeyboardButton("🏰 Menu Principal", callback_data="menu_principal")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open(caminho_foto_pet, 'rb') as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto_sucesso),
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        await query.edit_message_caption(
            caption=f"⚠️ (Imagem {pet['imagem']} não encontrada)\n\n{texto_sucesso}",
            reply_markup=reply_markup
        )

    
async def pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    jogador = database.get_jogador(user_id) 
    
    if not jogador or jogador["pet_nome"] is None:
        await query.edit_message_caption("❌ Você ainda não tem um pet.")
        return

    # Busca XP necessário para o nível atual do pet
    xp_prox_lvl = database.calcular_xp_pet(jogador['pet_level'])
    
    itens = database.get_inventario(user_id)
    item_maca = next((i for i in itens if i['item_nome'] == "Maçã"), None)
    qtd_maca = item_maca['quantidade'] if item_maca else 0

    arquivo_imagem = jogador["pet_imagem"] if jogador["pet_imagem"] else "capa.png"
    caminho_foto = os.path.join('imagens', arquivo_imagem)

    texto = (
        f"🐾 Pet: {jogador['pet_nome']} (Lvl {jogador['pet_level']})\n\n"
        f"✨ XP: {jogador['pet_xp']}/{xp_prox_lvl}\n"
        f"❤️ Vida: {jogador['pet_vida']}\n"
        f"⚔️ Ataque: {jogador['pet_ataque']}\n"
        f"🛡️ Defesa: {jogador['pet_defesa']}\n"
        f"⚡ Agilidade: {jogador['pet_agilidade']}"
    )

    keyboard = []
    botoes_alimento = []
    if qtd_maca >= 1: botoes_alimento.append(InlineKeyboardButton("🍎 x1", callback_data="dar_maca_1"))
    if qtd_maca >= 10: botoes_alimento.append(InlineKeyboardButton("🍎 x10", callback_data="dar_maca_10"))
    if qtd_maca >= 20: botoes_alimento.append(InlineKeyboardButton("🍎 x20", callback_data="dar_maca_20"))
    
    if botoes_alimento: keyboard.append(botoes_alimento)
    keyboard.append([InlineKeyboardButton("⬅ Voltar", callback_data="menu")])
    
    try:
        with open(caminho_foto, 'rb') as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto, parse_mode="Markdown"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")  
        
    
async def voltar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    jogador = database.get_jogador(user_id)
    
    if not jogador:
        await menu_principal(update, context)
        return

    # No SQLite com Row, acessamos pelo nome da coluna
    mapa_id = jogador['mapa_atual']

    if mapa_id == 0:
        # Se está na vila (0), volta para o menu principal
        await menu_principal(update, context)
    else:
        # Se está em outro mapa, chama a função que desenha o mapa
        # Lembra que criamos a função 'exibir_mapa' no arquivo viagem.py?
        from handlers.viagem import exibir_mapa
        await exibir_mapa(update, context, mapa_id)


async def login_diario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Recupera o personagem logado na sessão
    nick = context.user_data.get("login_nick")
    
    if not nick:
        # Se falhar, tentamos a outra chave só por segurança
        nick = context.user_data.get("personagem_logado")

    if not nick:
        await query.edit_message_caption("❌ Você precisa estar logado para resgatar o bônus.")
        return

    # Chama a lógica do banco
    sucesso, mensagem = database.reivindicar_login_diario(nick)

    # Cria o botão de voltar
    keyboard = [[InlineKeyboardButton("⬅ Voltar ao Menu", callback_data="menu_principal")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if sucesso:
        await query.edit_message_caption(f"🎁 LOGIN DIÁRIO\n\n{mensagem}", reply_markup=reply_markup)
    else:
        # Se já resgatou, exibe a mensagem de aviso
        await query.edit_message_caption(f"⏳ AVISO\n\n{mensagem}", reply_markup=reply_markup)
        

async def dar_maca_pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    # O callback_data é "dar_maca_10". split("_") gera ['dar', 'maca', '10']
    # O índice [2] é o '10'
    try:
        dados = query.data.split("_")
        qtd = int(dados[2])
    except (IndexError, ValueError):
        qtd = 1

    # CHAMADA IMPORTANTE: Certifique-se de que passa os 4 valores
    sucesso, mensagem = database.dar_xp_pet(user_id, "Maçã", 10, qtd)
    
    if not sucesso:
        await query.answer(mensagem, show_alert=True)
        return

    await query.answer(mensagem) 
    await pet(update, context) # Recarrega a tela do Pet