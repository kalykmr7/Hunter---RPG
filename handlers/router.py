
import handlers.cadastro as cadastro
import handlers.login as login

async def processar_texto(update, context):

    user_id = update.effective_user.id
    
    print("🔥 ROUTER FOI CHAMADO")

    # LOGIN TEM PRIORIDADE
    if context.user_data.get("login_etapa"):
        await login.processar_login(update, context)
        return

    # CADASTRO
    if context.user_data.get("esperando_nick") or context.user_data.get("esperando_senha"):
        await cadastro.processar_texto_cadastro(update, context)
        return