from telegram import Update
from telegram.ext import ContextTypes
import database

async def ver_perfil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nick = context.user_data.get("personagem_logado")
    if not nick:
        await update.message.reply_text("❌ Você não está logado.")
        return

    dados_brutos = database.buscar_personagem_por_nick(nick)
    # APLICA O BÔNUS AQUI
    dados = database.aplicar_bonus_pet(dict(dados_brutos)) 

    xp_prox_lvl = database.calcular_xp_necessario(dados['level'])
    emoji = "♂️" if dados["genero"] == "masculino" else "♀️"
    
    mensagem = (
        f"📜 Perfil\n\n"
        f"👤 Nick: {dados['nick']}\n"
        f"⚥ Gênero: {dados['genero'].capitalize()} {emoji}\n"
        f"❤️ Vida: {dados['vida']}/{dados['vida_max']}\n" 
        f"💰 Gold: {dados['gold']}\n"  
        f"⭐ Nível: {dados['level']}\n"
        f"🧪 XP: {dados['xp']}/{xp_prox_lvl}\n"
        f"⚔️ Ataque: {dados['ataque']}\n"
        f"🛡️ Defesa: {dados['defesa']}\n"
    )

    await update.message.reply_text(mensagem, parse_mode="Markdown")
    