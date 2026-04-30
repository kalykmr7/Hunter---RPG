# --- ARQUIVO: .\handlers\router.py ---
import handlers.cadastro as cadastro
import handlers.login as login
import database
import admin
from modelos.monstros import buscar_modelo_pet
from modelos.itens import buscar_dados_item

ADMIN_ID = 5386405631  


async def processar_texto(update, context):
    user_id = update.effective_user.id
    texto = update.message.text
    comando_limpo = texto.lower()

    # --- COMANDO ADMIN: /dar [NICK] [QTD] [NOME] ---
    if (comando_limpo.startswith("dar ") or comando_limpo.startswith("/dar ")) and user_id == ADMIN_ID:
        partes = texto.split()
        
        if len(partes) < 4:
            await update.message.reply_text("⚠️ Use: `/dar [NICK] [QTD] [NOME]`\nEx: `/dar Recruta 10 Maçã`", parse_mode="Markdown")
            return

        nick_alvo = partes[1]
        try:
            quantidade = int(partes[2])
        except ValueError:
            await update.message.reply_text("❌ A quantidade deve ser um número.")
            return
            
        nome_item = " ".join(partes[3:]) # Pega o resto como nome do item

        # 1. Verifica se o jogador existe
        jogador = database.buscar_personagem_por_nick(nick_alvo)
        if not jogador:
            await update.message.reply_text(f"❌ Jogador '{nick_alvo}' não encontrado.")
            return

        # 2. Verifica se o item existe na lista mestre
        dados_item = buscar_dados_item(nome_item)
        if not dados_item:
            await update.message.reply_text(f"❌ Item '{nome_item}' não existe no jogo.")
            return

        # 3. Adiciona ao inventário no banco
        sucesso, msg = database.adicionar_item_inventario(
            jogador['user_id'], 
            dados_item['nome'], 
            dados_item['tipo'], 
            quantidade
        )

        if sucesso:
            await update.message.reply_text(f"✅ Feito! {quantidade}x {dados_item['nome']} enviados para {nick_alvo}.")
        else:
            await update.message.reply_text(f"⚠️ Ocorreu um problema: {msg}")
        return

    # --- COMANDO ADMIN: /darpet ---
    if (comando_limpo.startswith("darpet ") or comando_limpo.startswith("/darpet ")) and user_id == ADMIN_ID:
        # (Mantenha a lógica do darpet que fizemos antes aqui)
        pass

    # --- COMANDO ADMIN: /set_level ---
    if (comando_limpo.startswith("set_level ") or comando_limpo.startswith("/set_level ")) and user_id == ADMIN_ID:
        # (Mantenha a sua lógica de set_level aqui)
        pass

    # --- LÓGICA DE LOGIN/CADASTRO ---
    if context.user_data.get("login_etapa"):
        await login.processar_login(update, context)
        return

    if context.user_data.get("esperando_nick") or context.user_data.get("esperando_senha"):
        await cadastro.processar_texto_cadastro(update, context)
        return