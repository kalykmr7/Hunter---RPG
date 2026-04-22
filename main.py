# Aqui é o motor do bot
import database
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import TOKEN
from handlers import start, cadastro
from handlers import perfil, menu
from handlers import login, router
from handlers import status as handler_status
from handlers import viagem, caca

print('Bot Online!')

def main():
    database.criar_tabela()
    database.atualizar_estrutura_banco()
    database.debug_tabela()
    app = Application.builder().token(TOKEN).build()

    # Handlers (Ouvintes)
    app.add_handler(CommandHandler("start", start.inicio))
    app.add_handler(CallbackQueryHandler(login.iniciar_login, pattern='^login$'))
    app.add_handler(CallbackQueryHandler(cadastro.escolher_genero, pattern='^registrar$'))
    app.add_handler(CallbackQueryHandler(cadastro.confirmar_genero, pattern="^genero_"))
    app.add_handler(CommandHandler("perfil", perfil.ver_perfil))
    app.add_handler(CallbackQueryHandler(start.resgatar_presente, pattern="resgatar_presente"))
    app.add_handler(CallbackQueryHandler(start.chocar_ovo, pattern="chocar_ovo"))
    app.add_handler(CallbackQueryHandler(menu.menu_principal, pattern="^menu_principal$"))
    app.add_handler(CallbackQueryHandler(start.pet, pattern="pet"))
    app.add_handler(CallbackQueryHandler(start.voltar_menu, pattern="menu"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,router.processar_texto))
    app.add_handler(CommandHandler("sair", login.sair_conta))
    app.add_handler(CallbackQueryHandler(start.login_diario, pattern="^login_diario$"))
    app.add_handler(CallbackQueryHandler(handler_status.status, pattern="status"))
    app.add_handler(CallbackQueryHandler(viagem.mostrar_mapas, pattern="^mapas$"))
    app.add_handler(CallbackQueryHandler(viagem.aviso_bloqueado, pattern="^mapa_bloqueado$"))
    app.add_handler(CallbackQueryHandler(viagem.entrar_no_mapa, pattern="^ir_"))
    app.add_handler(CallbackQueryHandler(caca.procurar_monstro, pattern="^procurar_"))
    app.add_handler(CallbackQueryHandler(caca.voltar_ao_mapa, pattern="^voltar_mapa$"))
    app.add_handler(CallbackQueryHandler(caca.atacar_turno, pattern="^atacar_turno$"))
    app.add_handler(CallbackQueryHandler(caca.voltar_ao_mapa, pattern="^fugir_luta$"))
    
    
    # ... outros handlers

    app.run_polling()

if __name__ == '__main__':
    main()
    