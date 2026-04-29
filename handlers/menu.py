from telegram import Update
from telegram.ext import ContextTypes
import database
from handlers.viagem import exibir_mapa # Importamos a função que centraliza tudo

async def menu_principal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Verifica se o personagem está logado na sessão
    nick = context.user_data.get("personagem_logado")
    
    if not nick:
        # Se não houver sessão, manda para o início
        print("DEBUG MENU: Nick não encontrado na sessão!")
        if update.callback_query:
            await update.callback_query.answer("Sessão expirada!", show_alert=True)
        return

    print("DEBUG MENU: Chamando exibir_mapa...")
    await exibir_mapa(update, context, 0)
    print("DEBUG MENU: exibir_mapa finalizado.")
    