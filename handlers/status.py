#Status do player

import os
import database
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

# --- ARQUIVO: .\handlers\status.py ---

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    database.curar_personagem_total(user_id)
    
    # BUSCA O JOGADOR E APLICA O BÔNUS AQUI
    jogador_bruto = database.get_jogador(user_id)
    jogador = database.aplicar_bonus_pet(dict(jogador_bruto)) # APLICA BÔNUS!
    print(f"DEBUG STATUS: Vida Max após bônus: {jogador['vida_max']}")

    if not jogador:
        await query.edit_message_caption(caption="❌ Erro: Personagem não encontrado.")
        return
    
    genero = jogador['genero'] 
    nome_arquivo = f"{genero}.png"
    caminho_imagem = os.path.join('imagens', nome_arquivo)

    xp_prox_lvl = database.calcular_xp_necessario(jogador['level'])
    
    # Texto formatado com os valores JÁ COM BÔNUS
    texto_status = (
        f"📊 STATUS\n\n"
        f"👤 Nick: {jogador['nick']}\n"
        f"📈 Nível: {jogador['level']}\n"
        f"🧪 XP: {jogador['xp']}/{xp_prox_lvl}\n"
        f"❤️ Vida: {jogador['vida_max']} \n" 
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