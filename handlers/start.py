# Comando /start e Menu principal

import os
import database
from database import aplicar_bonus_pet
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
    jogador_bruto = database.get_jogador(user_id) 
    
    if not jogador_bruto or not jogador_bruto["pet_nome"]:
        await query.edit_message_caption("❌ Você ainda não tem um pet.")
        return
    
    # Aplica o bônus
    jogador = database.aplicar_bonus_pet(dict(jogador_bruto))

    # Verifica quantas maçãs o jogador tem para o botão aparecer
    itens = database.get_inventario(user_id)
    qtd_maca = sum(item['quantidade'] for item in itens if item['item_nome'] == "Maçã")

    arquivo_imagem = jogador["pet_imagem"] if jogador["pet_imagem"] else "capa.png"
    caminho_foto = os.path.join('imagens', arquivo_imagem)
    
    status_eq = "✅ Equipado" if jogador['pet_equipado'] == 1 else "❌ Desequipado"
    label_eq = "Desequipar" if jogador['pet_equipado'] == 1 else "Equipar"

    texto = (
        f"🐾 Pet: {jogador['pet_nome']} (Lvl {jogador['pet_level']})\n"
        f"Status: {status_eq}\n\n"
        f"❤️ Vida Max: {jogador['vida_max']}\n"
        f"⚔️ Ataque: {jogador['ataque']}\n"
        f"🛡️ Defesa: {jogador['defesa']}\n\n"
        f"🍎 Maçãs disponíveis: {qtd_maca}"
    )

    keyboard = [
        [InlineKeyboardButton(f"{label_eq}", callback_data="equipar_pet")]
    ]
    
    # Se tiver maçã, mostra o botão de alimentar
    if qtd_maca > 0:
        keyboard.append([InlineKeyboardButton(f"Alimentar", callback_data="alimentar_menu")])
        
    keyboard.append([InlineKeyboardButton("⬅ Voltar", callback_data="menu")])
    
    try:
        with open(caminho_foto, 'rb') as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto, parse_mode="Markdown"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        await query.edit_message_caption(
            caption=f"⚠️ Imagem não encontrada\n\n{texto}", 
            reply_markup=InlineKeyboardMarkup(keyboard), 
            parse_mode="Markdown"
        )
        
    
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
        

async def alimentar_pet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra opções de quantidade baseada no estoque de maçãs"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    itens = database.get_inventario(user_id)
    qtd_total = sum(item['quantidade'] for item in itens if item['item_nome'] == "Maçã")
    
    if qtd_total == 0:
        await query.answer("Você não tem maçãs!", show_alert=True)
        return

    # Monta botões baseados no que o jogador possui
    keyboard = []
    
    if qtd_total >= 1: keyboard.append([InlineKeyboardButton(" Alimentar com 1x", callback_data="exec_alim_1")])
    if qtd_total >= 10: keyboard.append([InlineKeyboardButton(" Alimentar com 10x", callback_data="exec_alim_10")])
    if qtd_total >= 20: keyboard.append([InlineKeyboardButton(" Alimentar com 20x", callback_data="exec_alim_20")])
    if qtd_total > 1: keyboard.append([InlineKeyboardButton(f" Tudo ({qtd_total}x)", callback_data=f"exec_alim_{qtd_total}")])
    
    keyboard.append([InlineKeyboardButton("⬅ Voltar ao Pet", callback_data="pet")])
    
    await query.edit_message_caption(
        caption=f"Menu de Alimentação\n\nVocê possui {qtd_total} maçãs. Escolha quanto dar ao seu pet:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    
    
async def executar_alimentar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe a escolha de quantidade e executa no banco"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # Extrai o número do callback (exec_alim_X)
    qtd = int(query.data.split("_")[2])
    
    sucesso, mensagem = database.dar_xp_pet(user_id, "Maçã", 10, qtd)
    
    # Resultado visual
    await query.answer(f"{'Sucesso!' if sucesso else 'Erro!'}")
    
    # Mostra mensagem e volta pro menu pet
    await pet(update, context)
    
    
    
async def equipar_pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    # Busca o estado atual no banco
    jogador = database.get_jogador(user_id)
    novo_estado = 1 if jogador['pet_equipado'] == 0 else 0
    
    # Atualiza no banco
    conn = database.conectar()
    conn.execute("UPDATE personagens SET pet_equipado = ? WHERE user_id = ?", (novo_estado, user_id))
    conn.commit()
    conn.close()
    
    await query.answer("Equipamento atualizado!")
    # Recarrega a tela do pet
    await pet(update, context)