# handlers/mochila.py

import os
import database
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

# handlers/mochila.py

import os
import database
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes


async def ver_mochila(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    itens = database.get_inventario(user_id)
    jogador = database.get_jogador(user_id)
    
    texto_equipamentos = "⚔️ Equipamentos\n"
    texto_consumiveis = "Itens e Consumíveis\n"
    
    tem_equip = False
    tem_cons = False
    keyboard = []

    if not itens:
        texto_final = "🎒 Mochila\n\nSua mochila está vazia... 🕸️"
    else:
        for item in itens:
            nome = item['item_nome']
            qtd = item['quantidade']
            tipo = item['tipo']

            if tipo == 'equipamento':
                tem_equip = True
                texto_equipamentos += f"🔹 {nome}\n"
            else:
                tem_cons = True
                texto_consumiveis += f"🔹 {nome} (x{qtd})\n"

        texto_final = "🎒 Mochila\n\n"
        if tem_equip:
            texto_final += texto_equipamentos + "\n"
        if tem_cons:
            texto_final += texto_consumiveis

    # Botão voltar dinâmico
    mapa_atual = jogador['mapa_atual'] if jogador else 0
    callback_volta = "menu_principal" if mapa_atual == 0 else f"ir_{mapa_atual}"
    keyboard.append([InlineKeyboardButton("⬅ Voltar", callback_data=callback_volta)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    caminho_img = os.path.join("imagens", "capa.png")

    try:
        with open(caminho_img, "rb") as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto_final, parse_mode="Markdown"),
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        await query.edit_message_caption(caption=texto_final, reply_markup=reply_markup, parse_mode="Markdown")
        
