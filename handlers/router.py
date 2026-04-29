# --- ARQUIVO: .\handlers\router.py ---
import handlers.cadastro as cadastro
import handlers.login as login
import database
import admin

ADMIN_ID = 5386405631  

async def processar_texto(update, context):
    user_id = update.effective_user.id
    texto = update.message.text
    
    # DEBUG: Isso vai aparecer no seu console quando você digitar qualquer coisa
    print(f"DEBUG ROTEADOR: Recebi texto '{texto}' de {user_id}")
    print(f"DEBUG ROTEADOR: Estados atuais -> {context.user_data}")

    # --- COMANDO DE ADMIN ---
    comando_limpo = texto.lower()
    if (comando_limpo.startswith("dar ") or comando_limpo.startswith("/dar ")) and user_id == ADMIN_ID:
        # ... (seu código de dar item continua igual)
        pass 

    # --- COMANDO ADMIN: /set_level ---
    if (comando_limpo.startswith("set_level ") or comando_limpo.startswith("/set_level ")) and user_id == ADMIN_ID:
        # ... (seu código de set_level continua igual)
        pass

    # --- LÓGICA DE LOGIN ---
    if context.user_data.get("login_etapa"):
        print("DEBUG ROTEADOR: Identificado etapa de login, chamando login.processar_login")
        await login.processar_login(update, context)
        return

    # --- LÓGICA DE CADASTRO ---
    if context.user_data.get("esperando_nick") or context.user_data.get("esperando_senha"):
        print("DEBUG ROTEADOR: Identificado etapa de cadastro, chamando cadastro.processar_texto_cadastro")
        await cadastro.processar_texto_cadastro(update, context)
        return
        
    print("DEBUG ROTEADOR: Nenhuma etapa de login ou cadastro encontrada.")