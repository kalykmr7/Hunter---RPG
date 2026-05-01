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

    # --- COMANDO ADMIN: /dar [NICK] [QTD] [ITEM] ---
    if (comando_limpo.startswith("dar ") or comando_limpo.startswith("/dar ")) and user_id == ADMIN_ID:
        # ... (Sua lógica de dar item que já funciona)
        from modelos.itens import buscar_dados_item
        partes = texto.split()
        if len(partes) >= 4:
            nick_alvo = partes[1]
            quantidade = int(partes[2])
            nome_item = " ".join(partes[3:])
            jogador = database.buscar_personagem_por_nick(nick_alvo)
            dados_item = buscar_dados_item(nome_item)
            if jogador and dados_item:
                database.adicionar_item_inventario(jogador['user_id'], dados_item['nome'], dados_item['tipo'], quantidade)
                await update.message.reply_text(f"✅ {quantidade}x {nome_item} dados para {nick_alvo}.")
        return

    # --- LÓGICA DE LOGIN E CADASTRO ---
    if context.user_data.get("login_etapa"):
        await login.processar_login(update, context)
        return

    if context.user_data.get("esperando_nick") or context.user_data.get("esperando_senha"):
        await cadastro.processar_texto_cadastro(update, context)
        return