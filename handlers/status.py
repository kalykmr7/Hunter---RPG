#Status do player

import os
import database
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    
    # 1. Busca os dados do jogador no banco
    jogador = database.get_jogador(user_id)

    if jogador is None:
        await query.edit_message_caption(caption="❌ Erro: Personagem não encontrado.")
        return

    # 2. Lógica da Imagem baseada no Gênero
    # Se o gênero for 'masculino', busca 'masculino.png'. Se 'feminino', busca 'feminino.png'
    genero = jogador['genero'] 
    nome_arquivo = f"{genero}.png"
    caminho_imagem = os.path.join('imagens', nome_arquivo)

    # 3. Montagem do Texto de Status
    texto_status = (
        f"📊 STATUS\n\n"
        f"👤 Nick: {jogador['nick']}\n"
        f"📈 Nível: {jogador['level']}\n"
        f"🧪 XP: {jogador['xp']}/100\n"
        f"❤️ Vida: {jogador['vida']}\n"
        f"⚔️ Ataque: {jogador['ataque']}\n"
        f"🛡️ Defesa: {jogador['defesa']}\n"
        f"💰 Gold: {jogador['gold']}\n"
        f"💎 Mithril: {jogador['mithril']}\n"
    )
    
    # 4. Botão Voltar Inteligente
    # Ele identifica onde você está para te devolver para o lugar certo
    mapa_atual = jogador['mapa_atual']
    
    # Se estiver na Vila (0), volta para o menu principal. Se não, volta para o mapa de caça.
    callback_volta = "menu_principal" if mapa_atual == 0 else f"ir_{mapa_atual}"
    
    keyboard = [[InlineKeyboardButton("⬅️ VOLTAR", callback_data=callback_volta)]]

    # 5. Envio com troca de imagem
    try:
        with open(caminho_imagem, 'rb') as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto_status, parse_mode="Markdown"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        # Se você esqueceu de colocar a imagem masculino.png ou feminino.png na pasta
        await query.edit_message_caption(
            caption=f"⚠️ (Imagem {nome_arquivo} não encontrada)\n\n{texto_status}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )