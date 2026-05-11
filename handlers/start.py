# Comando /start e Menu principal

import os
import database
from database import aplicar_bonus_pet
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from modelos.monstros import sortear_pet
from handlers.menu import menu_principal
from handlers import viagem
from datetime import datetime

async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Log de diagnóstico
    user_id = update.effective_user.id
    print(f"DEBUG: Comando /start recebido do user {user_id}")
    
    database.resetar_localizacao(user_id)
    
    keyboard = [
        [
            InlineKeyboardButton("⚔️ Criar Conta", callback_data='registrar'),
            InlineKeyboardButton("Fazer Login", callback_data='login')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    texto = "Bem-vindo ao Reino de Hunter 🏰\nSua jornada começa agora."

    # IMPORTANTE: Verifique se a pasta se chama 'imagens' (minúsculo) no GitHub
    caminho_imagem = os.path.join("imagens", "capa.png")

    try:
        if os.path.exists(caminho_imagem):
            with open(caminho_imagem, "rb") as foto:
                await update.effective_chat.send_photo(
                    photo=foto,
                    caption=texto,
                    reply_markup=reply_markup
                )
        else:
            print(f"DEBUG: Arquivo não encontrado em {caminho_imagem}")
            await update.effective_chat.send_message(
                text=texto + "\n\n⚠️ (Imagem não encontrada no servidor)",
                reply_markup=reply_markup
            )

    except Exception as e:
        print(f"ERRO CRÍTICO NO START: {e}")
        await update.effective_chat.send_message(
            text=f"Erro ao iniciar o bot: {e}",
            reply_markup=reply_markup
        )

# 🥚 OVO
async def resgatar_presente(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    caminho_imagem = os.path.join('imagens', 'ovo.png')

    try:
        with open(caminho_imagem, 'rb') as foto:
            from telegram import InputMediaPhoto

            await query.edit_message_media(
                media=InputMediaPhoto(
                    media=foto,
                    caption="🎁 Você encontrou um ovo misterioso...\n\nClique para chocar!"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🥚 Chocar ovo", callback_data="chocar_ovo")]
                ])
            )

    except FileNotFoundError:
        await query.edit_message_caption(
            caption="🎁 Ovo misterioso...\n\nClique para chocar!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🥚 Chocar ovo", callback_data="chocar_ovo")]
            ])
        )


# 🐣 CHOCAR OVO
async def chocar_ovo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    from modelos.monstros import sortear_pet
    pet = sortear_pet() 

    # Adiciona à nova tabela de pets
    database.adicionar_novo_pet(user_id, pet)
    
    # Marca que o jogo iniciou na tabela principal
    conn = database.conectar()
    conn.execute("UPDATE personagens SET jogo_iniciado = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    caminho_foto_pet = os.path.join('imagens', pet["imagem"])
    texto_sucesso = (
        f"🎉 O OVO CHOCOU!\n\n"
        f"🐾 Você obteve: {pet['nome']}\n"
        f"Ele foi adicionado à sua coleção! Você pode gerenciar seus pets no menu Pet."
    )

    keyboard = [[InlineKeyboardButton("🏰 Menu Principal", callback_data="menu_principal")]]
    
    try:
        with open(caminho_foto_pet, 'rb') as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto_sucesso),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        await query.edit_message_caption(caption=texto_sucesso, reply_markup=InlineKeyboardMarkup(keyboard))

    
async def pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu principal de Pets com botão para Incubadora."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    pets = database.get_pets_jogador(user_id)
    
    texto = "🐾 Galeria de Pet\nGerencie seus companheiros ou choque novos ovos!\n"
    keyboard = []
    
    # BOTÃO DA INCUBADORA (Sempre visível)
    keyboard.append([InlineKeyboardButton("🥚 Incubadora", callback_data="abrir_incubadora")])
    
    if pets:
        texto += "\nSua Coleção:\n"
        for p in pets:
            status = "✅" if p['equipado'] else "💤"
            keyboard.append([InlineKeyboardButton(f"{status} {p['nome']} (Lvl {p['level']})", callback_data=f"ver_pet_{p['id']}")])
    
    keyboard.append([InlineKeyboardButton("⬅ Voltar", callback_data="menu")])
    await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    

    
async def voltar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    jogador = database.get_jogador(user_id)
    
    if not jogador:
        await menu_principal(update, context)
        return

    # No SQLite com Row, acessamos pelo nome da coluna
    mapa_id = jogador['mapa_atual']

    if mapa_id == 0:
        # Se está na vila (0), volta para o menu principal
        await menu_principal(update, context)
    else:
        # Se está em outro mapa, chama a função que desenha o mapa
        # Lembra que criamos a função 'exibir_mapa' no arquivo viagem.py?
        from handlers.viagem import exibir_mapa
        await exibir_mapa(update, context, mapa_id)


async def login_diario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    nick = context.user_data.get("personagem_logado")

    # 1. Lógica do Login Diário (Bônus de Ouro)
    resgate_ok, msg_login = database.reivindicar_login_diario(nick) if nick else (False, "Faça login.")

    # 2. Busca Missões Diárias
    missoes = database.get_ou_criar_missoes(user_id)
    
    texto = f"🎁 Bônus diário\n{msg_login}\n\n"
    texto += "📜 Missões de hoje\n"
    
    keyboard = []
    
    for m in missoes:
        status = "✅" if m['reivindicada'] else "🎯"
        # MAPEAMENTO DE NOMES
        nomes = {
            'caca': f"Caçar {m['objetivo']} monstros",
            'gold': f"Ganhar {m['objetivo']} gold caçando",
            'pocao': f"Usar {m['objetivo']} poções em luta",
            'forja': f"Realizar {m['objetivo']} melhorias no Ateliê",
            'venda': f"Vender {m['objetivo']} itens no Ateliê",
            'alimentar': f"Dar {m['objetivo']} frutas ao Pet"
        }
        desc = nomes.get(m['tipo'], "Missão desconhecida")
        
        texto += f"{status} {desc} ({m['progresso']}/{m['objetivo']})\n"
        
        # Se completou mas não reivindicou, mostra o botão
        if m['progresso'] >= m['objetivo'] and not m['reivindicada']:
            keyboard.append([InlineKeyboardButton(f"🎁 Resgatar {m['recompensa_gold']} Gold", callback_data=f"resgatar_missao_{m['tipo']}")])

    keyboard.append([InlineKeyboardButton("⬅ Voltar", callback_data="menu_principal")])
    
    await query.edit_message_caption(
        caption=texto, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def reivindicar_missao_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para o botão de resgate da missão"""
    query = update.callback_query
    user_id = query.from_user.id
    tipo = query.data.replace("resgatar_missao_", "")
    
    sucesso, msg = database.reivindicar_missao_db(user_id, tipo)
    await query.answer(msg, show_alert=True)
    
    # Atualiza a tela de login diário para mostrar o status novo
    await login_diario(update, context)
    


async def alimentar_pet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra opções de quantidade para o pet selecionado"""
    query = update.callback_query
    await query.answer()
    
    # Extrai o pet_id do callback (ex: alimentar_menu_5)
    pet_id = int(query.data.split("_")[2])
    user_id = query.from_user.id
    
    itens = database.get_inventario(user_id)
    qtd_total = sum(item['quantidade'] for item in itens if item['item_nome'] == "Fruta arco-íris")
    
    if qtd_total == 0:
        await query.answer("Você não tem nenhuma fruta!", show_alert=True)
        return

    keyboard = []
    # O callback agora leva o pet_id e a quantidade: exec_alim_{pet_id}_{qtd}
    if qtd_total >= 1: keyboard.append([InlineKeyboardButton("🍎 1x Fruta arco-íris", callback_data=f"exec_alim_{pet_id}_1")])
    if qtd_total >= 10: keyboard.append([InlineKeyboardButton("🍎 10x frutas arco-íris", callback_data=f"exec_alim_{pet_id}_10")])
    if qtd_total > 1: keyboard.append([InlineKeyboardButton(f"🍎 Tudo ({qtd_total}x)", callback_data=f"exec_alim_{pet_id}_{qtd_total}")])
    
    keyboard.append([InlineKeyboardButton("⬅ Voltar", callback_data=f"ver_pet_{pet_id}")])
    
    await query.edit_message_caption(
        caption=f"Quantas frutas arco-íris deseja dar ao seu pet?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    
async def executar_alimentar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executa a alimentação no pet específico"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Extrai dados: exec_alim_{pet_id}_{qtd}
    partes = query.data.split("_")
    pet_id = int(partes[2])
    qtd = int(partes[3])
    
    sucesso, mensagem = database.dar_xp_pet(user_id, pet_id, "Fruta arco-íris", 10, qtd)
    
    await query.answer(mensagem, show_alert=True)
    database.atualizar_progresso_missao(user_id, 'alimentar', qtd)
    
    # Retorna para a tela de detalhes do pet para ver o progresso
    # Criamos um objeto query "fake" para reaproveitar a função ver_detalhes_pet
    query.data = f"ver_pet_{pet_id}"
    await ver_detalhes_pet(update, context)
    
    
    
async def equipar_pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    # Busca o estado atual no banco
    jogador = database.get_jogador(user_id)
    novo_estado = 1 if jogador['pet_equipado'] == 0 else 0
    
    # Atualiza no banco
    conn = database.conectar()
    conn.execute("UPDATE personagens SET pet_equipado = ? WHERE user_id = ?", (novo_estado, user_id))
    conn.commit()
    conn.close()
    
    await query.answer("Equipamento atualizado!")
    # Recarrega a tela do pet
    await pet(update, context)
    
    
async def ver_detalhes_pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe detalhes do pet com alternância real entre Equipar/Desequipar"""
    query = update.callback_query
    await query.answer()
    
    # Extração do ID
    pet_id = int(query.data.split("_")[2])
    pet_db = database.get_pet_por_id(pet_id)
    user_id = query.from_user.id
    
    if not pet_db:
        await query.edit_message_caption("❌ Pet não encontrado.")
        return

    # Busca descrição do bônus
    from modelos.monstros import buscar_modelo_pet
    modelo = buscar_modelo_pet(pet_db['nome'])
    desc_bonus = modelo.get('bonus', "Bônus não configurado.")

    # SEGURANÇA: Convertemos para int para garantir a comparação (1 ou 0)
    esta_equipado = int(pet_db['equipado']) == 1
    status_texto = "✅ EQUIPADO" if esta_equipado else "💤"
    
    texto = (
        f"🐾 Detalhes\n\n"
        f"Nome: {pet_db['nome']}\n"
        f"Nível: {pet_db['level']}\n"
        f"Status: {status_texto}\n\n"
        f"✨ Habilidade: \n{desc_bonus}\n\n"
        f"📊 Status: \n❤️ {pet_db['vida']} | ⚔️ {pet_db['ataque']} | 🛡️ {pet_db['defesa']}"
    )

    keyboard = []
    
    # LÓGICA DO BOTÃO DINÂMICO
    if esta_equipado:
        # Se está equipado, mostra apenas o botão de DESEQUIPAR
        keyboard.append([InlineKeyboardButton("❌ Desequipar Pet", callback_data=f"desequipar_pet_{pet_id}")])
    else:
        # Se NÃO está equipado, mostra o botão de EQUIPAR
        keyboard.append([InlineKeyboardButton("⚔️ Equipar este Pet", callback_data=f"equipar_pet_{pet_id}")])

    # Botão de alimentação (sempre visível se houver maçãs)
    itens = database.get_inventario(user_id)
    qtd_maca = sum(item['quantidade'] for item in itens if item['item_nome'] == "Fruta arco-íris")
    if qtd_maca > 0:
        keyboard.append([InlineKeyboardButton(f"🍎 Alimentar ({qtd_maca})", callback_data=f"alimentar_menu_{pet_id}")])
        
    keyboard.append([InlineKeyboardButton("⬅ Voltar", callback_data="pet")])
    
    caminho_foto = os.path.join('imagens', pet_db['imagem'])
    
    try:
        with open(caminho_foto, 'rb') as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto, parse_mode="Markdown"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        

async def executar_equipar_pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a troca de pet ativo"""
    query = update.callback_query
    user_id = query.from_user.id
    pet_id = int(query.data.split("_")[2])
    
    # Chama a função do banco que criamos no passo anterior
    database.equipar_pet_db(user_id, pet_id)
    
    await query.answer("🐾 Pet equipado com sucesso!", show_alert=True)
    
    # Volta para os detalhes do pet atualizado
    await ver_detalhes_pet(update, context)
    

async def executar_desequipar_pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executa a remoção do pet ativo"""
    query = update.callback_query
    user_id = query.from_user.id
    pet_id = int(query.data.split("_")[2]) # Pegamos o ID apenas para recarregar a tela depois
    
    # Chama a função do banco
    database.desequipar_pet_completo_db(user_id)
    
    await query.answer("Desequipado", show_alert=True)
    
    # Recarrega a tela de detalhes para mostrar que agora o status mudou
    await ver_detalhes_pet(update, context)
    
    
async def abrir_incubadora(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    MAX_SLOTS = 3 
    processos = database.get_incubacoes_ativas(user_id)
    ovos_estoque = database.get_ovos_jogador(user_id)
    
    texto = f"🌡️ Central de Incubação ({len(processos)}/{MAX_SLOTS})\n\n"
    keyboard = []

    # OVOS CHOCANDO
    if processos:
        for p in processos:
            tempo_final = datetime.strptime(p['tempo_final'], "%Y-%m-%d %H:%M:%S")
            agora = datetime.now()
            
            if agora >= tempo_final:
                texto += f"✅ {p['ovo_nome']} pronto!\n"
                keyboard.append([InlineKeyboardButton(f"🐣 Reivindicar {p['ovo_nome']}", callback_data=f"finalizar_chocar_{p['id']}")])
            else:
                restante = tempo_final - agora
                texto += f"⏳ {p['ovo_nome']}: `{restante.seconds // 3600:02}h` restantes\n"
        keyboard.append([InlineKeyboardButton("🔄 Atualizar", callback_data="abrir_incubadora")])
    else:
        texto += "❄️ Nenhuma incubação ativa.\n"

    # ESTOQUE
    texto += "\n📦 Seus Ovos:\n"
    if not ovos_estoque:
        texto += "_Vazio._"
    else:
        for o in ovos_estoque:
            # Exibe o nome completo: Ovo [Região 1]
            texto += f"• {o['item_nome']} (x{o['quantidade']})\n"
            if len(processos) < MAX_SLOTS:
                keyboard.append([InlineKeyboardButton(f"🔥 Chocar {o['item_nome']}", callback_data=f"chocar_selecionado_{o['id']}")])

    keyboard.append([InlineKeyboardButton("⬅ Voltar", callback_data="pet")])
    await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")




async def chocar_ovo_selecionado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o processo de chocar com base na raridade."""
    query = update.callback_query
    user_id = query.from_user.id
    inv_id = int(query.data.split("_")[2])
    
    conn = database.conectar()
    ovo = conn.execute("SELECT item_nome FROM inventario WHERE id = ? AND user_id = ?", (inv_id, user_id)).fetchone()
    if not ovo:
        conn.close()
        return

    nome_ovo = ovo['item_nome']
    
    # DEFINIÇÃO DE TEMPOS (REGRAS DO MESTRE)
    tempos = {
        "Ovo Comum": 6,
        "Ovo Incomum": 12,
        "Ovo Raro": 18,
        "Ovo Lendário": 24
    }
    horas_necessarias = tempos.get(nome_ovo, 6)

    # 1. Consome o ovo da mochila
    conn.execute("UPDATE inventario SET quantidade = quantidade - 1 WHERE id = ?", (inv_id,))
    conn.execute("DELETE FROM inventario WHERE id = ? AND quantidade <= 0", (inv_id,))
    conn.commit()
    conn.close()

    # 2. Inicia o timer no banco
    database.iniciar_incubacao_db(user_id, nome_ovo, horas_necessarias)
    
    await query.answer(f"O {nome_ovo} foi colocado na incubadora! 🌡️", show_alert=True)
    await abrir_incubadora(update, context)
    

async def finalizar_chocar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    incubacao_id = int(query.data.split("_")[2])
    
    conn = database.conectar()
    res = conn.execute("SELECT ovo_nome FROM incubacao_ativa WHERE id = ?", (incubacao_id,)).fetchone()
    conn.close()
    
    if not res: return

    nome_do_ovo = res['ovo_nome']
    mapa_id = 0
    # Extrai o número de: Ovo [Região 3]
    if "Região " in nome_do_ovo:
        try:
            mapa_id = int(nome_do_ovo.split("Região ")[1].replace("]", ""))
        except: mapa_id = 0

    from modelos.monstros import sortear_pet
    pet_ganho = sortear_pet(mapa_id)
    database.adicionar_novo_pet(user_id, pet_ganho)
    database.remover_incubacao_por_id(incubacao_id)
    
    await query.answer(f"Nasceu um {pet_ganho['nome']}!")
    
    texto = f"🎉 O OVO CHOCOU!\n\n🐾 Você obteve: {pet_ganho['nome']}\n✨ Bônus: _{pet_ganho['bonus']}_"
    keyboard = [[InlineKeyboardButton(" Voltar", callback_data="abrir_incubadora")]]
    
    caminho_foto = os.path.join('imagens', pet_ganho['imagem'])
    try:
        with open(caminho_foto, 'rb') as foto:
            await query.edit_message_media(media=InputMediaPhoto(media=foto, caption=texto, parse_mode="Markdown"), reply_markup=InlineKeyboardMarkup(keyboard))
    except:
        await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")