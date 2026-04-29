# --- ARQUIVO: .\handlers\router.py ---
import handlers.cadastro as cadastro
import handlers.login as login
import database
import admin

ADMIN_ID = 5386405631  

async def processar_texto(update, context):
    user_id = update.effective_user.id
    texto = update.message.text

    # --- COMANDO DE ADMIN ---
    comando_limpo = texto.lower()
    if (comando_limpo.startswith("dar ") or comando_limpo.startswith("/dar ")) and user_id == ADMIN_ID:
        # ... (seu código de dar item continua igual)
        pass 

    # --- COMANDO ADMIN: /set_level ---
    if (comando_limpo.startswith("set_level ") or comando_limpo.startswith("/set_level ")) and user_id == ADMIN_ID:
        # Divide a mensagem: ['/set_level', 'nick_do_usuario', 'novo_nivel']
        partes = texto.split()
        
        if len(partes) < 3:
            await update.message.reply_text("⚠️ Formato incorreto. Use: /set_level [NICK] [NIVEL]")
            return

        nick_alvo = partes[1]
        try:
            nivel_novo = int(partes[2])
            # Chama a função que importamos lá em cima no admin.py
            sucesso = admin.set_level_admin(nick_alvo, nivel_novo)
            
            if sucesso:
                await update.message.reply_text(f"✅ Sucesso! O jogador {nick_alvo} agora está no Nível {nivel_novo}.")
            else:
                await update.message.reply_text(f"❌ Erro: Jogador '{nick_alvo}' não encontrado.")
        except ValueError:
            await update.message.reply_text("⚠️ O nível deve ser um número inteiro.")
        return

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