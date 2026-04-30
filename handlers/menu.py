from telegram import Update
from telegram.ext import ContextTypes
import handlers.viagem as viagem

async def menu_principal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Busca o nick na sessão
    nick = context.user_data.get("personagem_logado")
    
    if not nick:
        print("DEBUG MENU: Erro - personagem_logado não está no user_data")
        return

    print(f"DEBUG MENU: Abrindo mapa para {nick}")
    # O mapa 0 é a Vila Inicial
    await viagem.exibir_mapa(update, context, 0)