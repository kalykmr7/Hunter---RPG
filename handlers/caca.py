#Lógica da caça

import os
import random
import database
import asyncio  # Permite que o bot "espere" alguns segundos
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from modelos.inimigos import inimigos_por_mapa
from modelos.mapas import lista_mapas



async def procurar_monstro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    # 1. Busca os dados do jogador
    jogador = database.get_jogador(user_id)
    
    if not jogador:
        await query.answer("Personagem não encontrado.", show_alert=True)
        return
    
    mapa_id = jogador['mapa_atual']

    # 2. NOVIDADE: Sorteia o inimigo direto do Banco de Dados
    inimigo_db = database.get_monstro_aleatorio(mapa_id)
    
    if not inimigo_db:
        await query.answer("Nenhum monstro cadastrado para este mapa...")
        return

    # 3. Busca os drops do monstro no Banco de Dados
    drops_db = database.get_drops_monstro(inimigo_db['nome'])
    
    # Convertemos os drops do banco para o formato que o sistema de luta já entende
    lista_drops = []
    for d in drops_db:
        lista_drops.append({
            "item": d['item_nome'],
            "chance": d['chance'],
            "tipo": "consumivel" # Por enquanto, drops de monstros são consumíveis
        })

    # 4. SALVA O ESTADO DA LUTA (Usando os nomes das colunas do banco)
    context.user_data["luta"] = {
        "inimigo_nome": inimigo_db['nome'],
        "inimigo_vida": inimigo_db['vida'],
        "inimigo_vida_max": inimigo_db['vida'],
        "inimigo_atq": inimigo_db['ataque'],
        "inimigo_def": inimigo_db['defesa'],
        "inimigo_xp": inimigo_db['xp_recompensa'],
        "inimigo_gold": inimigo_db['gold_recompensa'],
        "inimigo_img": inimigo_db['imagem'],
        "inimigo_drops": lista_drops,
        "player_vida": jogador['vida'],
        "mapa_id": mapa_id
    }

    # 5. Interface Inicial
    texto = (
        f"⚔️ Uma criatura apareceu!\n\n"
        f"👾 Inimigo: {inimigo_db['nome']}\n"
        f"❤️ Vida: {inimigo_db['vida']}/{inimigo_db['vida']}\n\n"
        f"O que você vai fazer?"
    )

    itens_player = database.get_inventario(user_id)
    tem_pocao = any("Poção" in item['item_nome'] for item in itens_player)

    keyboard = [[InlineKeyboardButton("⚔️ Atacar", callback_data="atacar_turno")]]
    if tem_pocao:
        keyboard.append([InlineKeyboardButton("🧪 Usar poção", callback_data="luta_usar_pocao")])
    keyboard.append([InlineKeyboardButton("🏃 Fugir", callback_data="fugir_luta")])

    caminho_img = os.path.join("imagens", inimigo_db['imagem'])
    
    try:
        with open(caminho_img, "rb") as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto, parse_mode="Markdown"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        


# --- ARQUIVO: .\handlers\caca.py ---

async def atacar_turno(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executa o turno de ataque e oferece opção de caçar novamente em caso de vitória"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    luta = context.user_data.get("luta")
    
    if not luta:
        await query.edit_message_caption("❌ Erro: Luta não encontrada.")
        return

    jogador = database.get_jogador(user_id)

    # 1. ATAQUE DO JOGADOR
    dano_player = max(1, jogador['ataque'] - (luta['inimigo_def'] // 2))
    luta['inimigo_vida'] -= dano_player
    
    # --- BLOCO DE VITÓRIA ---
    if luta['inimigo_vida'] <= 0:
        novo_xp = jogador['xp'] + luta['inimigo_xp']
        novo_gold = jogador['gold'] + luta['inimigo_gold']
        
        itens_ganhos = []
        for drop in luta.get('inimigo_drops', []):
            if random.randint(1, 100) <= drop['chance']:
                sucesso, _ = database.adicionar_item_inventario(user_id, drop['item'], drop['tipo'])
                if sucesso: 
                    itens_ganhos.append(drop['item'])
                    break 

        conn = database.conectar()
        conn.execute("UPDATE personagens SET xp = ?, gold = ?, vida = ? WHERE user_id = ?", (novo_xp, novo_gold, luta['player_vida'], user_id))
        conn.commit()
        conn.close()

        texto_resultado = f"🏆 Vitória!\n\nVocê derrotou o {luta['inimigo_nome']}!\n💰 +{luta['inimigo_gold']} Gold | ✨ +{luta['inimigo_xp']} XP\n"
        if itens_ganhos: texto_resultado += f"🎁 Drop: {itens_ganhos[0]}\n"
        
        xp_necessario = database.calcular_xp_necessario(jogador['level'])
        if novo_xp >= xp_necessario:
            status_novos = database.subir_de_nivel(user_id)
            if status_novos: texto_resultado += f"\n🌟 LEVEL UP! Nível {status_novos['level']}!\n"

        # --- NOVIDADE: Teclado com duas opções ---
        keyboard = [
            [InlineKeyboardButton("⚔️ Caçar novamente", callback_data=f"procurar_{luta['mapa_id']}")],
            [InlineKeyboardButton("🏃 Voltar", callback_data=f"ir_{luta['mapa_id']}")]
        ]
        
        context.user_data["luta"] = None # Limpa a luta atual da memória
        
        await query.edit_message_caption(
            caption=texto_resultado, 
            reply_markup=InlineKeyboardMarkup(keyboard), 
            parse_mode="Markdown"
        )
        return

    # 2. TURNO DO MONSTRO
    texto_feedback = f"⚔️ Combate\n\n👤 Você causou {dano_player} de dano!\n⏳ O {luta['inimigo_nome']} está atacando..."
    await query.edit_message_caption(caption=texto_feedback, reply_markup=None, parse_mode="Markdown")
    
    await asyncio.sleep(1.2) 

    dano_monstro = max(1, luta['inimigo_atq'] - (jogador['defesa'] // 2))
    luta['player_vida'] -= dano_monstro

    conn = database.conectar()
    conn.execute("UPDATE personagens SET vida = ? WHERE user_id = ?", (max(0, luta['player_vida']), user_id))
    conn.commit()
    conn.close()

    # Check Derrota
    if luta['player_vida'] <= 0:
        texto_derrota = f"💀 DERROTA!\n\nO {luta['inimigo_nome']} te nocauteou!"
        keyboard = [[InlineKeyboardButton("🏰 Voltar para a Vila", callback_data="ir_0")]]
        context.user_data["luta"] = None
        await query.edit_message_caption(caption=texto_derrota, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    log = f"👤 Causou {dano_player} de dano\n👾 Recebeu {dano_monstro} de dano"
    await voltar_turno_luta(update, context, log)
    

async def usar_pocao_luta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Menu de seleção de poções
    texto_escolha = "🧪 *Menu de Alquimia*\n\nQual poção deseja usar?"

    keyboard = [
        [InlineKeyboardButton("🧪 Poção Pequena ( 20%)", callback_data="itemluta_Poção pequena")],
        [InlineKeyboardButton("🧪 Poção Média (50%)", callback_data="itemluta_Poção média")],
        [InlineKeyboardButton("🧪 Poção Grande (85%)", callback_data="itemluta_Poção grande")],
        [InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_turno_luta")]
    ]

    await query.edit_message_caption(
        caption=texto_escolha, 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="Markdown"
    )
    
    
async def voltar_ao_mapa(update, context):
    query = update.callback_query
    await query.answer("Você fugiu da luta!")
    
    user_id = query.from_user.id
    jogador = database.get_jogador(user_id)
    mapa_id = jogador['mapa_atual']
    
    context.user_data["luta"] = None # Limpa a luta ao fugir

    from handlers.viagem import exibir_mapa
    await exibir_mapa(update, context, mapa_id)
    
    
async def confirmar_cura_luta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    luta = context.user_data.get("luta")
    
    if not luta:
        await query.answer("Luta encerrada!")
        return

    # 1. Busca os dados atuais do jogador (precisamos da vida_max)
    jogador = database.get_jogador(user_id)
    vida_max_player = jogador['vida_max']

    # 2. Identifica o item e define a porcentagem
    item_escolhido = query.data.split("_")[1]
    
    porcentagens = {
        "poção pequena": 0.20,
        "poção média": 0.50,
        "poção grande": 0.85
    }
    
    multiplicador = porcentagens.get(item_escolhido.lower(), 0.20)
    
    # 3. CALCULA O VALOR REAL DA CURA
    # Ex: Se tiver 200 de vida max, poção média cura int(200 * 0.50) = 100
    valor_cura = int(vida_max_player * multiplicador)

    # 4. Tenta usar no banco (A função usar_pocao_cura já limita ao máximo de HP)
    sucesso, mensagem_banco = database.usar_pocao_cura(user_id, item_escolhido, valor_cura)

    if not sucesso:
        await query.answer(mensagem_banco, show_alert=True)
        return

    # 5. Atualiza a vida na memória da luta e avisa o jogador
    jogador_pos_cura = database.get_jogador(user_id)
    luta['player_vida'] = jogador_pos_cura['vida'] 

    await query.answer(f"Cura aplicada: +{valor_cura} HP!")
    
    texto_feedback = (
        f"💉 Você usou {item_escolhido}!\n"
        f"✨ Recuperou {valor_cura} HP.\n"
        f"❤️ Vida: {luta['player_vida']}/{vida_max_player}\n\n"
        f"⏳ O {luta['inimigo_nome']} está atacando..."
    )
    
    await query.edit_message_caption(caption=texto_feedback, reply_markup=None, parse_mode="Markdown")

    # Turno do Inimigo (Contra-ataque)
    await asyncio.sleep(1.5)
    
    dano_monstro = max(1, luta['inimigo_atq'] - (jogador_pos_cura['defesa'] // 2))
    luta['player_vida'] -= dano_monstro

    # Sincroniza o dano sofrido com o Banco de Dados
    conn = database.conectar()
    conn.execute("UPDATE personagens SET vida = ? WHERE user_id = ?", (max(0, luta['player_vida']), user_id))
    conn.commit()
    conn.close()

    if luta['player_vida'] <= 0:
        keyboard = [[InlineKeyboardButton("🏰 Voltar", callback_data="ir_0")]]
        context.user_data["luta"] = None
        await query.edit_message_caption(
            caption=f"💀 O {luta['inimigo_nome']} te nocauteou!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await voltar_turno_luta(update, context)


async def voltar_turno_luta(update: Update, context: ContextTypes.DEFAULT_TYPE, log_combate=""):
    """Reconstrói o menu de ataque exibindo o log de dano"""
    query = update.callback_query
    user_id = query.from_user.id
    luta = context.user_data.get("luta")
    
    if not luta: return

    jogador = database.get_jogador(user_id)
    itens = database.get_inventario(user_id)
    # Verificação robusta de poção
    tem_pocao = any("poção" in i['item_nome'].lower() for i in itens)

    keyboard = [[InlineKeyboardButton("⚔️ Atacar", callback_data="atacar_turno")]]
    if tem_pocao:
        keyboard.append([InlineKeyboardButton("🧪 Usar poção", callback_data="luta_usar_pocao")])
    keyboard.append([InlineKeyboardButton("🏃 Fugir", callback_data="fugir_luta")])

    # CORREÇÃO 1: Preparando o texto do log para aparecer na mensagem
    log_texto = f"📝 Último Turno:\n_{log_combate}_\n\n" if log_combate else ""

    texto = (
        f"⚔️ Combate em andamento\n\n"
        f"{log_texto}"
        f"👾 {luta['inimigo_nome']}: ❤️ {luta['inimigo_vida']}/{luta['inimigo_vida_max']}\n"
        f"👤 Você: ❤️ {luta['player_vida']}/{jogador['vida_max']}\n\n"
        f"Sua vez! O que vai fazer?"
    )

    await query.edit_message_caption(
        caption=texto, 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="Markdown"
    )