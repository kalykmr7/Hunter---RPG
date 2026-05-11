import database
import admin
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import TOKEN
from handlers import start, cadastro, perfil, menu, login, router, status as handler_status, viagem, caca, mochila, atelie
import warnings

# Configuração de Logging para ver erros no console da Shard Cloud
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore", category=UserWarning)

def main():
    # Inicialização do Banco em ordem logica
    database.criar_tabela()                     #Cria o que nao existe
    database.criar_tabela_incubadora()          #Cria tabela para incubadora
    database.criar_tabela_missoes()             #Cria a tabela de missoes diarias
    database.atualizar_estrutura_banco()        #Adiciona colunas novas em bancos antigos
    database.popular_dados_iniciais()           #Insere dados dos modelos
    admin.debug_tabela()                        #debug
    
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
    app.add_handler(MessageHandler(filters.TEXT, router.processar_texto))
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
    app.add_handler(CallbackQueryHandler(start.alimentar_pet_menu, pattern="^alimentar_menu_"))
    app.add_handler(CallbackQueryHandler(start.executar_alimentar, pattern="^exec_alim_"))
    app.add_handler(CallbackQueryHandler(start.ver_detalhes_pet, pattern="^ver_pet_"))
    app.add_handler(CallbackQueryHandler(start.executar_equipar_pet, pattern="^equipar_pet_"))
    app.add_handler(CallbackQueryHandler(mochila.detalhes_item, pattern="^item_ver_"))
    app.add_handler(CallbackQueryHandler(mochila.executar_acao_item, pattern="^item_acao_"))
    app.add_handler(CallbackQueryHandler(start.executar_desequipar_pet, pattern="^desequipar_pet_"))
    app.add_handler(CallbackQueryHandler(atelie.menu_atelie, pattern="^atelie_menu$"))
    app.add_handler(CallbackQueryHandler(atelie.listar_venda, pattern="^atelie_vender_lista_"))
    app.add_handler(CallbackQueryHandler(atelie.executar_venda, pattern="^confirmar_venda_"))
    app.add_handler(CallbackQueryHandler(atelie.menu_forja, pattern="^atelie_forja_menu$"))
    app.add_handler(CallbackQueryHandler(atelie.executar_forja, pattern="^executar_forja_"))
    app.add_handler(CallbackQueryHandler(atelie.detalhes_forja_item, pattern="^forja_ver_"))
    app.add_handler(CallbackQueryHandler(start.reivindicar_missao_callback, pattern="^resgatar_missao_"))
    app.add_handler(CallbackQueryHandler(start.abrir_incubadora, pattern="^abrir_incubadora$"))
    app.add_handler(CallbackQueryHandler(start.chocar_ovo_selecionado, pattern="^chocar_selecionado_"))
    app.add_handler(CallbackQueryHandler(start.finalizar_chocar_callback, pattern="^finalizar_chocar_"))
    app.add_handler(CallbackQueryHandler(atelie.menu_alquimia, pattern="^alquimia_menu$"))
    app.add_handler(CallbackQueryHandler(atelie.executar_alquimia, pattern="^exec_alquimia_"))
    app.add_handler(CallbackQueryHandler(atelie.listar_venda, pattern="^atelie_vender_lista_"))
    app.add_handler(CallbackQueryHandler(atelie.vender_detalhes_item, pattern="^vender_ver_"))
    app.add_handler(CallbackQueryHandler(atelie.executar_venda, pattern="^vender_exec_"))
    
    
    # drop_pending_updates=True limpa comandos antigos que foram enviados enquanto o bot estava off
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
        main()
        
