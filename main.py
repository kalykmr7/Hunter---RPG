import database
import admin
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import TOKEN
from handlers import start, cadastro, perfil, menu, login, router, status as handler_status, viagem, caca, mochila
import warnings

# Configuração de Logging para ver erros no console da Shard Cloud
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore", category=UserWarning)

print("--- SISTEMA INICIADO ---")

def main():
    # Inicialização do Banco
    database.criar_tabela()
    database.popular_dados_iniciais()
    database.atualizar_estrutura_banco()
    admin.debug_tabela()
    
    # Construção do App
    app = Application.builder().token(TOKEN).build()

    # Handlers
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router.processar_texto))
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
    app.add_handler(CallbackQueryHandler(caca.usar_pocao_luta, pattern="^luta_usar_pocao$"))
    app.add_handler(CallbackQueryHandler(caca.confirmar_cura_luta, pattern="^itemluta_"))
    app.add_handler(CallbackQueryHandler(caca.voltar_turno_luta, pattern="^voltar_turno_luta$"))
    app.add_handler(CallbackQueryHandler(mochila.ver_mochila, pattern="^mochila$"))
    app.add_handler(CallbackQueryHandler(start.equipar_pet, pattern="^equipar_pet$"))
    app.add_handler(CallbackQueryHandler(start.alimentar_pet_menu, pattern="^alimentar_menu$"))
    app.add_handler(CallbackQueryHandler(start.executar_alimentar, pattern="^exec_alim_"))

    print("Bot aguardando mensagens...")
    
    # drop_pending_updates=True limpa comandos antigos que foram enviados enquanto o bot estava off
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()