from telegram import Update
from telegram.ext import ContextTypes
import database
# Usamos a importação direta para evitar problemas de circularidade
import handlers.menu as menu

async def iniciar_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["login_etapa"] = "nick"
    await query.edit_message_caption("🔐 LOGIN\n\nDigite seu Nick:")
    
async def processar_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    etapa = context.user_data.get("login_etapa")

    if etapa == "nick":
        context.user_data["login_nick"] = update.message.text
        context.user_data["login_etapa"] = "senha"
        await update.message.reply_text("🔑 Agora digite sua senha:")
        return

    elif etapa == "senha":
        nick = context.user_data.get("login_nick")
        senha_digitada = update.message.text.strip()
        jogador = database.buscar_personagem_por_nick(nick)
        
        if not jogador:
            await update.message.reply_text("❌ Personagem não encontrado.")
            context.user_data.clear()
            return

        senha_banco = jogador['senha']

        if str(senha_banco) == str(senha_digitada):
            print(f"DEBUG LOGIN: Sucesso para {nick}. Chamando menu...")
            # Limpa dados temporários de login mas mantém o essencial
            context.user_data.clear()
            context.user_data["personagem_logado"] = nick 
            
            await update.message.reply_text(f"✅ Login OK! Bem-vindo, {nick}!")
            
            # Chama o menu principal explicitamente
            await menu.menu_principal(update, context)
        else:
            await update.message.reply_text("❌ Senha incorreta.")
            context.user_data.clear()

async def sair_conta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🔓 Você saiu da conta.\n\nUse /start para fazer login novamente.")