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
    # Log de diagnóstico
    user_id = update.effective_user.id
    print(f"DEBUG: Comando /start recebido do user {user_id}")
    
    database.resetar_localizacao(user_id)
    
    keyboard = [
        [
            InlineKeyboardButton("⚔️ Criar Conta", callback_data='registrar'),
            InlineKeyboardButton("Fazer Login", callback_data='login')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    texto = "Bem-vindo ao Reino de Hunter 🏰\nSua jornada começa agora."

    # IMPORTANTE: Verifique se a pasta se chama 'imagens' (minúsculo) no GitHub
    caminho_imagem = os.path.join("imagens", "capa.png")

    try:
        if os.path.exists(caminho_imagem):
            with open(caminho_imagem, "rb") as foto:
                await update.effective_chat.send_photo(
                    photo=foto,
                    caption=texto,
                    reply_markup=reply_markup
                )
        else:
            print(f"DEBUG: Arquivo não encontrado em {caminho_imagem}")
            await update.effective_chat.send_message(
                text=texto + "\n\n⚠️ (Imagem não encontrada no servidor)",
                reply_markup=reply_markup
            )

    except Exception as e:
        print(f"ERRO CRÍTICO NO START: {e}")
        await update.effective_chat.send_message(
            text=f"Erro ao iniciar o bot: {e}",
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
    
    from modelos.monstros import sortear_pet
    pet = sortear_pet() 

    # Adiciona à nova tabela de pets
    database.adicionar_novo_pet(user_id, pet)
    
    # Marca que o jogo iniciou na tabela principal
    conn = database.conectar()
    conn.execute("UPDATE personagens SET jogo_iniciado = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    caminho_foto_pet = os.path.join('imagens', pet["imagem"])
    texto_sucesso = (
        f"🎉 O OVO CHOCOU!\n\n"
        f"🐾 Você obteve: {pet['nome']}\n"
        f"Ele foi adicionado à sua coleção! Você pode gerenciar seus pets no menu de Pet."
    )

    keyboard = [[InlineKeyboardButton("🏰 Menu Principal", callback_data="menu_principal")]]
    
    try:
        with open(caminho_foto_pet, 'rb') as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto_sucesso),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        await query.edit_message_caption(caption=texto_sucesso, reply_markup=InlineKeyboardMarkup(keyboard))

    
async def pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    pets = database.get_pets_jogador(user_id)
    
    if not pets:
        await query.edit_message_caption("❌ Você ainda não tem pets.")
        return

    texto = "🐾 *SUA COLEÇÃO DE PETS*\n\nEscolha um pet para ver detalhes ou equipar:\n"
    keyboard = []
    
    for p in pets:
        status = "✅" if p['equipado'] else "💤"
        keyboard.append([InlineKeyboardButton(
            f"{status} {p['nome']} (Lvl {p['level']})", 
            callback_data=f"ver_pet_{p['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("⬅ Voltar", callback_data="menu")])
    
    await query.edit_message_caption(
        caption=texto, 
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
    
    
async def ver_detalhes_pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe os detalhes de um pet específico da coleção"""
    query = update.callback_query
    await query.answer()
    
    # Extrai o ID do pet do callback (ex: ver_pet_5 -> 5)
    pet_id = int(query.data.split("_")[2])
    pet = database.get_pet_por_id(pet_id)
    user_id = query.from_user.id
    
    if not pet:
        await query.edit_message_caption("❌ Pet não encontrado.")
        return

    # Verifica se tem maçãs para mostrar o botão alimentar
    itens = database.get_inventario(user_id)
    qtd_maca = sum(item['quantidade'] for item in itens if item['item_nome'] == "Maçã")

    status_eq = "✅ Equipado" if pet['equipado'] else [ ]
    
    texto = (
        f"🐾 Detalhes do pet:\n\n"
        f"Nome: {pet['nome']}\n"
        f"Nível: {pet['level']}\n"
        f"Status: {status_eq}\n\n"
        f"❤️ Vida: {pet['vida']}\n"
        f"⚔️ Ataque: {pet['ataque']}\n"
        f"🛡️ Defesa: {pet['defesa']}\n"
        f"⚡ Agilidade: {pet['agilidade']}\n\n"
        f"🍎 Suas maçãs: {qtd_maca}"
    )

    keyboard = []
    
    # Se não estiver equipado, mostra o botão para equipar
    if not pet['equipado']:
        keyboard.append([InlineKeyboardButton("⚔️ Equipar este Pet", callback_data=f"equipar_pet_{pet_id}")])
    
    # Botão de alimentar (usamos o ID do pet agora para o XP ir para o lugar certo!)
    if qtd_maca > 0:
        keyboard.append([InlineKeyboardButton("🍎 Alimentar", callback_data=f"alimentar_menu_{pet_id}")])
        
    keyboard.append([InlineKeyboardButton("⬅ Voltar para Lista", callback_data="pet")])
    
    caminho_foto = os.path.join('imagens', pet['imagem'])
    
    try:
        with open(caminho_foto, 'rb') as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto, parse_mode="Markdown"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def executar_equipar_pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a troca de pet ativo"""
    query = update.callback_query
    user_id = query.from_user.id
    pet_id = int(query.data.split("_")[2])
    
    # Chama a função do banco que criamos no passo anterior
    database.equipar_pet_db(user_id, pet_id)
    
    await query.answer("🐾 Pet equipado com sucesso!", show_alert=True)
    
    # Volta para os detalhes do pet atualizado
    await ver_detalhes_pet(update, context)
    
