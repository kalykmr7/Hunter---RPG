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

    # ETAPA 1: nick
    if etapa == "nick":
        context.user_data["login_nick"] = update.message.text
        context.user_data["login_etapa"] = "senha"
        await update.message.reply_text("🔑 Agora digite sua senha:")
        return

    # ETAPA 2: senha
    elif etapa == "senha":
        nick = context.user_data.get("login_nick")
        senha_digitada = update.message.text.strip()

        jogador = database.buscar_personagem_por_nick(nick)
        
        if not jogador:
            print("DEBUG LOGIN: Jogador não encontrado.")
            await update.message.reply_text("❌ Personagem não encontrado.")
            return

        print(f"DEBUG LOGIN: Jogador encontrado. Tipo de dado: {type(jogador)}")
        
        try:
            # Vamos tentar acessar a senha de duas formas para garantir
            senha_banco = None
            
            # Tenta via Chave (sqlite3.Row)
            try:
                senha_banco = jogador['senha']
                print(f"DEBUG LOGIN: Senha obtida via chave ['senha']: {senha_banco}")
            except:
                # Tenta via índice (caso a row_factory falhe)
                senha_banco = jogador[4]
                print(f"DEBUG LOGIN: Senha obtida via índice [4]: {senha_banco}")

            if str(senha_banco) == str(senha_digitada):
                print("DEBUG LOGIN: Senha confere! Logando...")
                context.user_data.clear() 
                context.user_data["personagem_logado"] = nick 
                await update.message.reply_text(f"✅ Login OK! Bem-vindo, {nick}!")
                await menu.menu_principal(update, context)
            else:
                print(f"DEBUG LOGIN: Senha incorreta. Banco: '{senha_banco}' vs Digitada: '{senha_digitada}'")
                context.user_data.clear()
                await update.message.reply_text("❌ Senha incorreta.")

        except Exception as e:
            print(f"DEBUG LOGIN: OCORREU UM ERRO GRAVE NO LOGIN: {e}")
            await update.message.reply_text("❌ Erro interno no login. Verifique o console.")
            
async def sair_conta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🔓 Você saiu da conta.\n\nUse /start para fazer login novamente."
    )