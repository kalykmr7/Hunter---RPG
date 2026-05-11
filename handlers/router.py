import handlers.cadastro as cadastro
import handlers.login as login
import database
import admin
from modelos.monstros import buscar_modelo_pet 

# COLOQUE SEU ID REAL AQUI
ADMIN_ID = 5386405631  

async def processar_texto(update, context):
    user_id = update.effective_user.id
    texto = update.message.text
    comando_limpo = texto.lower()

    # --- COMANDO ADMIN: /darpet [NICK] [NOME DO PET] ---
    if comando_limpo.startswith(("/darpet ", "darpet ")) and user_id == ADMIN_ID:
        print(f"DEBUG ADMIN: Tentando dar pet. Comando: {texto}")
        
        partes = texto.split()
        if len(partes) < 3:
            await update.message.reply_text("⚠️ Use: `/darpet [NICK] [NOME]`\nEx: `/darpet Recruta Lobo filhote`", parse_mode="Markdown")
            return

        nick_alvo = partes[1]
        nome_pet = " ".join(partes[2:]) # Une o resto (ex: 'Lobo', 'filhote' -> 'Lobo filhote')
        
        # 1. Busca o modelo do pet nos monstros.py
        pet_modelo = buscar_modelo_pet(nome_pet)
        if not pet_modelo:
            print(f"DEBUG ADMIN: Pet '{nome_pet}' não encontrado nos modelos.")
            await update.message.reply_text(f"❌ O pet '{nome_pet}' não existe nos arquivos de modelos.")
            return

        # 2. Busca o jogador pelo Nick
        jogador_alvo = database.buscar_personagem_por_nick(nick_alvo)
        if not jogador_alvo:
            print(f"DEBUG ADMIN: Jogador '{nick_alvo}' não encontrado no banco.")
            await update.message.reply_text(f"❌ O jogador '{nick_alvo}' não foi encontrado.")
            return

        # 3. Entrega o pet
        target_id = jogador_alvo['user_id']
        database.adicionar_novo_pet(target_id, pet_modelo)
        
        print(f"DEBUG ADMIN: Pet {nome_pet} entregue para {nick_alvo} com sucesso!")
        await update.message.reply_text(f"✅ Sucesso! *{nome_pet}* foi adicionado à coleção de *{nick_alvo}*!", parse_mode="Markdown")
        return

    # --- COMANDO ADMIN: /dar [NICK] [QTD] [RECURSO/ITEM] ---
    if (comando_limpo.startswith("dar ") or comando_limpo.startswith("/dar ")) and user_id == ADMIN_ID:
        partes = texto.split()
        if len(partes) < 4:
            await update.message.reply_text("⚠️ Use: `/dar [NICK] [QTD] [ITEM ou GOLD]`")
            return

        nick_alvo = partes[1]
        try:
            quantidade = int(partes[2])
        except ValueError:
            await update.message.reply_text("⚠️ A quantidade deve ser um número.")
            return

        nome_alvo = " ".join(partes[3:])
        nome_alvo_lower = nome_alvo.lower()

        # 1. Se for recurso financeiro
        if nome_alvo_lower in ['gold', 'mithril']:
            sucesso, msg = admin.dar_recurso_admin(nick_alvo, nome_alvo_lower, quantidade)
            await update.message.reply_text(msg)
        
        # 2. Se for um item físico
        else:
            sucesso, msg = admin.dar_item_admin(nick_alvo, nome_alvo, quantidade)
            if sucesso:
                await update.message.reply_text(f"✅ Sucesso: {quantidade}x {nome_alvo} para {nick_alvo}.")
            else:
                await update.message.reply_text(f"❌ Erro: {msg}")
        return
    
    # --- COMANDO ADMIN: /set_level [NICK] [NIVEL] ---
    if comando_limpo.startswith(("/set_level", "set_level")):
        if user_id != ADMIN_ID:
            await update.message.reply_text("🚫 Acesso negado.")
            return

        partes = texto.split()
        if len(partes) < 3:
            await update.message.reply_text("⚠️ Use: `/set_level [NICK] [NIVEL]`")
            return

        nick_alvo = partes[1]
        try:
            nivel_novo = int(partes[2])
            # Chamada para a função no admin.py
            sucesso = admin.set_level_admin(nick_alvo, nivel_novo)
            
            if sucesso:
                await update.message.reply_text(f"✅ O jogador {nick_alvo} foi definido para o Nível {nivel_novo}!", parse_mode="Markdown")
            else:
                # Tenta buscar pelo nick exato (caso o usuário tenha digitado minúsculo)
                await update.message.reply_text(f"❌ Jogador '{nick_alvo}' não encontrado. Verifique se o Nick está idêntico ao jogo (Maiúsculas/Minúsculas).")
        except ValueError:
            await update.message.reply_text("⚠️ O nível deve ser um número inteiro.")
        return

    # --- LÓGICA DE LOGIN E CADASTRO ---
    if context.user_data.get("login_etapa"):
        await login.processar_login(update, context)
        return

    if context.user_data.get("esperando_nick") or context.user_data.get("esperando_senha"):
        await cadastro.processar_texto_cadastro(update, context)
        return