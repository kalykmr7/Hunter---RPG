# Lógica da caça

import os
import random
import database
import asyncio  
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

async def procurar_monstro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    # 1. BUSCA O JOGADOR E APLICA OS BÔNUS (EQUIPAMENTOS + PET)
    jogador_bruto = database.get_jogador(user_id)
    if not jogador_bruto: return
    
    # Transformamos em dicionário e aplicamos os bônus dinâmicos
    jogador = database.aplicar_bonus_geral(dict(jogador_bruto))
    
    # 2. CURA PARA O MÁXIMO REAL (COM BÔNUS)
    # Agora o seu HP no banco será atualizado para 320 (no seu exemplo)
    database.curar_personagem_custom(user_id, jogador['vida_max'])
    
    mapa_id = jogador['mapa_atual']
    inimigo_db = database.get_monstro_aleatorio(mapa_id)
    
    if not inimigo_db:
        await query.answer("Nenhum monstro nesta área...")
        return

    # 3. SALVA O ESTADO DA LUTA COM O HP CORRETO
    context.user_data["luta"] = {
        "inimigo_nome": inimigo_db['nome'],
        "inimigo_vida": inimigo_db['vida'],
        "inimigo_vida_max": inimigo_db['vida'],
        "inimigo_atq": inimigo_db['ataque'],
        "inimigo_def": inimigo_db['defesa'],
        "inimigo_xp": inimigo_db['xp_recompensa'],
        "inimigo_gold": inimigo_db['gold_recompensa'],
        "inimigo_img": inimigo_db['imagem'],
        "player_vida": jogador['vida_max'], # Começa com o HP total (320)
        "player_vida_max": jogador['vida_max'], # Guarda o limite real
        "mapa_id": mapa_id,
        "processando": False
    }

    texto = (
        f"⚔️Surge {inimigo_db['nome']} no seu caminho!\n\n"
        f"👾 HP: {inimigo_db['vida']}/{inimigo_db['vida']}\n"
        f"👤 Seu HP: {jogador['vida_max']}/{jogador['vida_max']}\n\n"
        f"Prepare-se para o combate!"
    )

    keyboard = [
        [InlineKeyboardButton("⚔️ Atacar", callback_data="atacar_turno")],
        [InlineKeyboardButton("🏃 Fugir", callback_data="fugir_luta")]
    ]

    caminho_img = os.path.join("imagens", inimigo_db['imagem'])
    try:
        with open(caminho_img, "rb") as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto, parse_mode="Markdown"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def atacar_turno(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executa o ataque com trava de segurança contra cliques duplos."""
    query = update.callback_query
    user_id = query.from_user.id
    luta = context.user_data.get("luta")
    
    if not luta:
        await query.answer("❌ Erro: Luta não encontrada.")
        return

    if luta.get('processando'):
        await query.answer("⏳ Aguarde o turno do oponente terminar!", show_alert=True)
        return

    luta['processando'] = True 
    await query.answer()

    jogador_base = database.get_jogador(user_id)
    jogador = database.aplicar_bonus_geral(jogador_base)

    # 1. ATAQUE DO JOGADOR
    dano_base_player = max(1, jogador['ataque'] - (luta['inimigo_def'] // 2))
    dano_final_player = int(dano_base_player * random.uniform(0.8, 1.2))
    luta['inimigo_vida'] -= dano_final_player
    
    if luta['inimigo_vida'] <= 0:
        luta['processando'] = False
        await processar_vitoria(query, context, jogador, luta, dano_final_player)
        return

    texto_feedback = (
        f"⚔️ Combate\n\n"
        f"👤 Você causou {dano_final_player} de dano!\n"
        f"⏳ {luta['inimigo_nome']} está contra-atacando..."
    )
    await query.edit_message_caption(caption=texto_feedback, reply_markup=query.message.reply_markup, parse_mode="Markdown")
    
    await asyncio.sleep(2.5) 

    # 2. TURNO DO MONSTRO
    dano_base_monstro = max(1, luta['inimigo_atq'] - (jogador['defesa'] // 2))
    dano_final_monstro = int(dano_base_monstro * random.uniform(0.8, 1.2))
    luta['player_vida'] -= dano_final_monstro

    # Sincroniza vida no banco
    conn = database.conectar()
    conn.execute("UPDATE personagens SET vida = ? WHERE user_id = ?", (max(0, luta['player_vida']), user_id))
    conn.commit()
    conn.close()

    if luta['player_vida'] <= 0:
        luta['processando'] = False
        texto_derrota = f"💀 Derrota!\n\nO {luta['inimigo_nome']} te venceu."
        keyboard = [[InlineKeyboardButton("Voltar para Vila", callback_data="ir_0")]]
        context.user_data["luta"] = None
        await query.edit_message_caption(caption=texto_derrota, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    luta['processando'] = False 
    log = f"Você causou {dano_final_player} de dano\nInimigo causou {dano_final_monstro} de dano"
    await voltar_turno_luta(update, context, log)

async def confirmar_cura_luta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cura o jogador e aguarda o contra-ataque com trava de turno."""
    query = update.callback_query
    user_id = query.from_user.id
    luta = context.user_data.get("luta")
    
    if not luta or luta.get('processando'):
        await query.answer("Aguarde!")
        return

    luta['processando'] = True
    
    #Pegar o jogador com bônus para calcular a porcentagem de cura real
    jogador_base = database.get_jogador(user_id)
    jogador = database.aplicar_bonus_geral(dict(jogador_base))
    
    item_escolhido = query.data.split("_")[1]
    
    porcentagens = {"poção pequena": 0.20, "poção média": 0.50, "poção grande": 0.85}
    multiplicador = porcentagens.get(item_escolhido.lower(), 0.20)
    
    # Valor de cura agora baseado no HP Máximo com Bônus
    valor_cura = int(jogador['vida_max'] * multiplicador)

    sucesso, mensagem_banco = database.usar_pocao_cura(user_id, item_escolhido, valor_cura)

    if not sucesso:
        luta['processando'] = False
        await query.answer(mensagem_banco, show_alert=True)
        return

    await query.answer(f"💉 Curou {valor_cura} HP!")
    luta['player_vida'] = database.get_jogador(user_id)['vida']
    database.atualizar_progresso_missao(user_id, 'pocao', 1)
    
    texto_feedback = f"💉 Você usou {item_escolhido}!\n⏳ O {luta['inimigo_nome']} aproveita tua guarda baixa para atacar..."
    await query.edit_message_caption(caption=texto_feedback, reply_markup=query.message.reply_markup, parse_mode="Markdown")
    
    await asyncio.sleep(2)
    
    jogador_bonus = database.aplicar_bonus_geral(database.get_jogador(user_id))
    dano_monstro = max(1, luta['inimigo_atq'] - (jogador_bonus['defesa'] // 2))
    luta['player_vida'] -= dano_monstro

    conn = database.conectar()
    conn.execute("UPDATE personagens SET vida = ? WHERE user_id = ?", (max(0, luta['player_vida']), user_id))
    conn.commit()
    conn.close()

    luta['processando'] = False
    if luta['player_vida'] <= 0:
        context.user_data["luta"] = None
        await query.edit_message_caption(caption="💀 Você foi nocauteado!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="ir_0")]]))
    else:
        await voltar_turno_luta(update, context, f"🧪 Curou {valor_cura} HP\nRecebeu {dano_monstro} de dano")

async def usar_pocao_luta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    luta = context.user_data.get("luta")
    if luta and luta.get('processando'):
        await query.answer("⏳ Aguarde o turno do oponente!", show_alert=True)
        return
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🧪 Poção Pequena (20%)", callback_data="itemluta_Poção pequena")],
        [InlineKeyboardButton("🧪 Poção Média (50%)", callback_data="itemluta_Poção média")],
        [InlineKeyboardButton("🧪 Poção Grande (85%)", callback_data="itemluta_Poção grande")],
        [InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_turno_luta")]
    ]
    await query.edit_message_caption(caption="Qual poção deseja usar?", reply_markup=InlineKeyboardMarkup(keyboard))

async def voltar_ao_mapa(update, context):
    """Função chamada ao fugir ou vencer para retornar ao mapa de origem."""
    query = update.callback_query
    user_id = query.from_user.id
    database.curar_personagem_total(user_id)
    jogador = database.get_jogador(user_id)
    mapa_id = jogador['mapa_atual']
    context.user_data["luta"] = None 

    from handlers.viagem import exibir_mapa
    await exibir_mapa(update, context, mapa_id)

async def voltar_turno_luta(update: Update, context: ContextTypes.DEFAULT_TYPE, log_combate=""):
    """Reconstrói o menu de ataque exibindo o HP Efetivo (com bônus)"""
    query = update.callback_query
    user_id = query.from_user.id
    luta = context.user_data.get("luta")
    
    if not luta: return

    itens = database.get_inventario(user_id)
    tem_pocao = any("poção" in i['item_nome'].lower() for i in itens)

    keyboard = [[InlineKeyboardButton("⚔️ Atacar", callback_data="atacar_turno")]]
    if tem_pocao:
        keyboard.append([InlineKeyboardButton("🧪 Usar poção", callback_data="luta_usar_pocao")])
    keyboard.append([InlineKeyboardButton("🏃 Fugir", callback_data="fugir_luta")])

    log_texto = f"📝 Último Turno:\n_{log_combate}_\n\n" if log_combate else ""

    # USAMOS luta['player_vida_max'] que salvamos no início para mostrar o limite real
    texto = (
        f"⚔️ Combate em andamento\n\n"
        f"{log_texto}"
        f"👾 {luta['inimigo_nome']}: ❤️ {luta['inimigo_vida']}/{luta['inimigo_vida_max']}\n"
        f"👤 Você: ❤️ {luta['player_vida']}/{luta['player_vida_max']}\n\n"
        f"Sua vez! O que vai fazer?"
    )

    await query.edit_message_caption(
        caption=texto, 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="Markdown"
    )

async def processar_vitoria(query, context, jogador, luta, dano_final):
    user_id = query.from_user.id
    
    # --- CÁLCULO DE BÔNUS DO PET ---
    bonus_xp = 1.0
    bonus_gold = 1.0
    
    if jogador.get('pet_equipado') == 1:
        nome_pet = jogador.get('pet_nome')
        if nome_pet == "Morcego de Ébano":
            bonus_xp = 1.10
        elif nome_pet == "Escopião de Bronze":
            bonus_gold = 1.10

    # Recompensas finais com bônus aplicado
    xp_final = int(luta['inimigo_xp'] * bonus_xp)
    gold_final = int(luta['inimigo_gold'] * bonus_gold)
    # --- FIM DOS BÔNUS ---

    database.atualizar_progresso_missao(user_id, 'caca', 1)
    database.atualizar_progresso_missao(user_id, 'gold', gold_final)
    
    novo_xp = jogador['xp'] + xp_final
    novo_gold = jogador['gold'] + gold_final
            
    item_dropado = database.get_drop_aleatorio(luta['mapa_id'])
    # Se for o pet Draco de Mica, a chance de drop extra de ovo é tratada aqui (Exemplo de lógica)
    ovo_dropado = database.sortear_ovo_diario(user_id, luta['mapa_id'])
    
    mensagem_drop = ""
    
    if item_dropado:
        from modelos.itens import buscar_dados_item
        dados = buscar_dados_item(item_dropado)
        database.adicionar_item_inventario(user_id, dados['nome'], dados['tipo'], 1)
        mensagem_drop += f"🎁 Drop: {item_dropado}\n"
        
    if ovo_dropado:
        # Adiciona o ovo específico (invisivelmente vinculado ao mapa)
        database.adicionar_item_inventario(user_id, ovo_dropado, 'consumivel', 1)
        # Na mensagem para o jogador, mostramos apenas "Ovo"
        mensagem_drop += f"🥚 EXTRA: Você encontrou um Ovo!\n"

    conn = database.conectar()
    conn.execute("UPDATE personagens SET xp = ?, gold = ?, vida = ? WHERE user_id = ?", 
                 (novo_xp, novo_gold, luta['player_vida'], user_id))
    conn.commit()
    conn.close()

    texto = (
        f"🏆 Vitória!!\n\n"
        f"Dano Final: {dano_final}\n"
        f"💰 +{luta['inimigo_gold']} Gold | ✨ +{luta['inimigo_xp']} XP\n"
        f"{mensagem_drop}"
    )
    
    if novo_xp >= database.calcular_xp_necessario(jogador['level']):
        status = database.subir_de_nivel(user_id)
        if status: texto += f"\n🌟 LEVEL UP! Nível {status['level']}!"

    keyboard = [
        [InlineKeyboardButton("⚔️ Caçar novamente", callback_data=f"procurar_{luta['mapa_id']}")],
        [InlineKeyboardButton("Voltar", callback_data=f"ir_{luta['mapa_id']}")]
    ]
    context.user_data["luta"] = None 
    await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

