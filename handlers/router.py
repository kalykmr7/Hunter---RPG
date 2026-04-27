
# handlers/router.py

import handlers.cadastro as cadastro
import handlers.login as login
import database

ADMIN_ID = 5386405631  

# --- ARQUIVO: .\handlers\router.py ---

async def processar_texto(update, context):
    user_id = update.effective_user.id
    texto = update.message.text
    
    # --- COMANDO DE ADMIN: dar [Qtd] [item] para [nick] ---
    comando_limpo = texto.lower()
    if (comando_limpo.startswith("dar ") or comando_limpo.startswith("/dar ")) and user_id == ADMIN_ID:
        if " para " not in comando_limpo:
            await update.message.reply_text("❌ Use: dar [Qtd] [Item] para [Nick]")
            return
        try:
            partes = texto.split(" para ")
            nick_destino = partes[1].strip()
            comando_item = partes[0].replace("dar ", "").replace("/dar ", "").strip()
            palavras = comando_item.split(" ")
            if palavras[0].isdigit():
                quantidade = int(palavras[0])
                nome_item = " ".join(palavras[1:]).strip().capitalize()
            else:
                quantidade = 1
                nome_item = comando_item.strip().capitalize()

            jogador_alvo = database.buscar_personagem_por_nick(nick_destino)
            if not jogador_alvo:
                await update.message.reply_text(f"❌ O Nick '{nick_destino}' não foi encontrado.")
                return

            tipo_item = "consumivel" if "Poção" in nome_item or "Maçã" in nome_item else "material"
            sucesso, mensagem_db = database.adicionar_item_inventario(jogador_alvo['user_id'], nome_item, tipo_item, quantidade)
            if sucesso:
                await update.message.reply_text(f"✅ Enviado {quantidade}x {nome_item} para {nick_destino}.")
            else:
                await update.message.reply_text(f"⚠️ Erro: {mensagem_db}")
        except Exception as e:
            await update.message.reply_text("❌ Erro ao processar o comando dar.")
        return

    # --- NOVO COMANDO ADMIN: /set_level [lvl] para [nick] ---
    if (comando_limpo.startswith("set_level ") or comando_limpo.startswith("/set_level ")) and user_id == ADMIN_ID:
        if " para " not in comando_limpo:
            await update.message.reply_text("❌ Use: /set_level [lvl] para [nick]")
            return
        try:
            partes = comando_limpo.split(" para ")
            nick_destino = partes[1].strip()
            # Pega o nível (remove o comando e limpa espaços)
            novo_lvl = int(partes[0].replace("set_level ", "").replace("/set_level ", "").strip())
            
            sucesso = database.set_level_admin(nick_destino, novo_lvl)
            if sucesso:
                await update.message.reply_text(f"⚡ Nível de *{nick_destino}* definido para {novo_lvl}!\nStatus escalonados com sucesso.", parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Nick não encontrado ou erro no banco.")
        except ValueError:
            await update.message.reply_text("❌ Nível deve ser um número.")
        return

    # --- RESTANTE DO CÓDIGO (LOGIN/CADASTRO) ---
    if context.user_data.get("login_etapa"):
        await login.processar_login(update, context)
        return

    if context.user_data.get("esperando_nick") or context.user_data.get("esperando_senha"):
        await cadastro.processar_texto_cadastro(update, context)
        return