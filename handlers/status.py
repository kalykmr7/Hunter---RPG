#Status do player

import os
import database
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    jogador = database.get_jogador(user_id)

    if jogador is None:
        await query.edit_message_caption(caption="❌ Erro: Personagem não encontrado.")
        return

    # --- NOVIDADE: Calcula o XP dinâmico ---
    xp_prox_lvl = database.calcular_xp_necessario(jogador['level'])

    genero = jogador['genero'] 
    nome_arquivo = f"{genero}.png"
    caminho_imagem = os.path.join('imagens', nome_arquivo)

    texto_status = (
        f"📊 Status\n\n"
        f"👤 Nick: {jogador['nick']}\n"
        f"📈 Nível: {jogador['level']}\n"
        f"🧪 XP: {jogador['xp']}/{xp_prox_lvl}\n" # Mudança aqui!
        f"❤️ Vida: {jogador['vida']}\n"
        f"⚔️ Ataque: {jogador['ataque']}\n"
        f"🛡️ Defesa: {jogador['defesa']}\n"
        f"💰 Gold: {jogador['gold']}\n"
        f"💎 Mithril: {jogador['mithril']}\n"
    )
    
    mapa_atual = jogador['mapa_atual']
    callback_volta = "menu_principal" if mapa_atual == 0 else f"ir_{mapa_atual}"
       
    keyboard = [
        [
        InlineKeyboardButton("🎒 Mochila", callback_data="mochila"),
        InlineKeyboardButton("⬅️ Voltar", callback_data=callback_volta)
        ]
    ]

    try:
        with open(caminho_imagem, 'rb') as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto_status, parse_mode="Markdown"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        await query.edit_message_caption(
            caption=f"⚠️ (Imagem {nome_arquivo} não encontrada)\n\n{texto_status}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )