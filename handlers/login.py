from telegram import Update
from telegram.ext import ContextTypes
import database
from handlers import menu


async def iniciar_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["login_etapa"] = "nick"

    await query.edit_message_caption(
        "🔐 LOGIN\n\nDigite seu Nick:"
    )
    
    
async def processar_login(update, context):

    etapa = context.user_data.get("login_etapa")

    print("🔥 LOGIN ETAPA:", etapa)
    print("🔥 LOGIN CHAMADO")
    print("ETAPA:", context.user_data.get("login_etapa"))
    print("TEXTO:", update.message.text)

    # ETAPA 1: nick
    if etapa == "nick":
        context.user_data["login_nick"] = update.message.text
        context.user_data["login_etapa"] = "senha"

        await update.message.reply_text("🔑 Agora digite sua senha:")
        return

    # ETAPA 2: senha
    elif etapa == "senha":
        nick = context.user_data.get("login_nick")
        senha = update.message.text

        jogador = database.buscar_personagem_por_nick(nick)

        # jogador[4] é onde está a senha no banco (de acordo com seu log)
        if jogador and jogador[4] == senha:
            # ✅ EM VEZ DE CLEAR, FAZEMOS ISSO:
            # 1. Removemos apenas as chaves de controle do login
            context.user_data.pop("login_etapa", None)
            context.user_data.pop("login_nick", None)

            # 2. CRIAMOS O CARIMBO DA SESSÃO (Essencial para o Menu)
            context.user_data["personagem_logado"] = nick 

            await update.message.reply_text(f"✅ Login OK! Bem-vindo, {nick}!")

            # 3. Agora o menu vai funcionar porque o "personagem_logado" existe!
            await menu.menu_principal(update, context)
            
        else:
            # Aqui tudo bem usar o clear se quiser resetar em caso de erro
            context.user_data.clear()
            await update.message.reply_text("❌ Dados inválidos (Nick ou Senha incorretos).")
            
async def sair_conta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🔓 Você saiu da conta.\n\nUse /start para fazer login novamente."
    )