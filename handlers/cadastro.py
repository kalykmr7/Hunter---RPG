# Lógica de gênero e Nick

usuarios_estado = {}

import sys
import database
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from handlers import start, menu


async def escolher_genero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    caminho_imagem = os.path.join('imagens', 'capa.png')

    keyboard = [
        [InlineKeyboardButton("Masculino ♂️", callback_data='genero_masculino')],
        [InlineKeyboardButton("Feminino ♀️", callback_data='genero_feminino')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    texto = "Para começar, qual o gênero do seu personagem?"

    try:
        with open(caminho_imagem, 'rb') as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto),
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        await query.edit_message_text(
            text=f"⚠️ (capa.png não encontrada)\n\n{texto}",
            reply_markup=reply_markup
        )


async def confirmar_genero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    genero_escolhido = query.data.split('_')[1]
    context.user_data['genero'] = genero_escolhido
    
    context.user_data["esperando_nick"] = True
    context.user_data["esperando_senha"] = False

    print("🔥 ESTADO SALVO:", context.user_data)

    nome_arquivo = f"{genero_escolhido}.png"
    caminho_imagem = os.path.join('imagens', nome_arquivo)

    texto = f"Gênero {genero_escolhido.capitalize()} escolhido! ✨\n\nAgora, digite o Nick do seu personagem:"

    user_id = query.from_user.id

    try:
        with open(caminho_imagem, 'rb') as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto),
                reply_markup=None
            )
    except FileNotFoundError:
        await query.edit_message_caption(
            caption=f"⚠️ (Imagem {nome_arquivo} não encontrada)\n\n{texto}",
            reply_markup=None
        )




async def processar_texto_cadastro(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # 👉 ETAPA 1: Nick
    if context.user_data.get("esperando_nick"):
        nick = update.message.text

        context.user_data["nick"] = nick
        context.user_data["esperando_nick"] = False
        context.user_data["esperando_senha"] = True

        await update.message.reply_text(
            f"🛡️ Nick definido: {nick}\n\nAgora digite sua senha:"
        )
        return

    # 👉 ETAPA 2: Senha
    if context.user_data.get("esperando_senha"):
        senha = update.message.text
        nick = context.user_data.get("nick")
        genero = context.user_data.get("genero")
        user_id = update.effective_user.id

        print(f"🔥 Tentando salvar: {nick} | {user_id}")

        sucesso = database.salvar_personagem(user_id, nick, genero, senha)

        if sucesso == True:
            context.user_data["esperando_nick"] = False
            context.user_data["esperando_senha"] = False
            context.user_data["personagem_logado"] = nick

            # Criamos o botão que vai ativar a função 'resgatar_presente' no start.py
            keyboard = [
                [InlineKeyboardButton("🎁 Resgatar Presente de Boas-vindas", callback_data="resgatar_presente")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"✅ Cadastro concluído!\n\n"
                f"👤 Nick: {nick}\n"
                f"⚥ Gênero: {genero.capitalize()}\n\n"
                f"🎁 Você recebeu um item especial de boas-vindas! Clique abaixo para abrir:",
                reply_markup=reply_markup
            )
            # REMOVEMOS a linha: await menu.menu_principal(update, context)
            return