from telegram import Update
from telegram.ext import ContextTypes
import database

async def ver_perfil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nick = context.user_data.get("personagem_logado")
    if not nick:
        await update.message.reply_text("❌ Você não está logado.")
        return

    dados = database.buscar_personagem_por_nick(nick)
    if not dados:
        await update.message.reply_text("❌ Personagem não encontrado.")
        return

    # --- NOVIDADE: Calcula o XP dinâmico para o nível atual ---
    xp_prox_lvl = database.calcular_xp_necessario(dados['level'])
    
    emoji = "♂️" if dados["genero"] == "masculino" else "♀️"
    
    mensagem = (
        f"📜 PERFIL\n\n"
        f"👤 Nick: {dados['nick']}\n"
        f"⚥ Gênero: {dados['genero'].capitalize()} {emoji}\n"
        f"❤️ Vida: {dados['vida']}/100\n" 
        f"💰 Gold: {dados['gold']}\n"  
        f"⭐ Nível: {dados['level']}\n"
        f"🧪 XP: {dados['xp']}/{xp_prox_lvl}\n" # Aqui mudamos de 100 para a variável
    )

    await update.message.reply_text(mensagem, parse_mode="Markdown")
    