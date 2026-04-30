#Lógica da caça

import os
import random
import database
import asyncio  
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

async def procurar_monstro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    # Cura o jogador para o padrão Arcade
    database.curar_personagem_total(user_id)
    jogador = database.get_jogador(user_id)
    
    if not jogador: return

    mapa_id = jogador['mapa_atual']
    inimigo_db = database.get_monstro_aleatorio(mapa_id)
    
    if not inimigo_db:
        await query.answer("Nenhum monstro nesta área...")
        return

    # SALVA O ESTADO DA LUTA (Repare que não salvamos mais drops aqui)
    context.user_data["luta"] = {
        "inimigo_nome": inimigo_db['nome'],
        "inimigo_vida": inimigo_db['vida'],
        "inimigo_vida_max": inimigo_db['vida'],
        "inimigo_atq": inimigo_db['ataque'],
        "inimigo_def": inimigo_db['defesa'],
        "inimigo_xp": inimigo_db['xp_recompensa'],
        "inimigo_gold": inimigo_db['gold_recompensa'],
        "inimigo_img": inimigo_db['imagem'],
        "player_vida": jogador['vida'],
        "mapa_id": mapa_id
    }

    texto = (
        f"⚔️ Um {inimigo_db['nome']} bloqueia seu caminho!\n\n"
        f"👾 HP: {inimigo_db['vida']}/{inimigo_db['vida']}\n"
        f"👤 Seu HP: {jogador['vida']}/{jogador['vida_max']}\n\n"
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
    """Executa o turno de ataque sem remover os botões para evitar 'pulos' na tela"""
    query = update.callback_query
    user_id = query.from_user.id
    luta = context.user_data.get("luta")
    
    if not luta:
        await query.answer("❌ Erro: Luta não encontrada.")
        return

    # --- BLOQUEIO DE SPAM ---
    if luta.get('processando'):
        await query.answer("⏳ Aguarde o turno do inimigo terminar!", show_alert=False)
        return

    await query.answer()
    luta['processando'] = True # Tranca o turno

    jogador_base = database.get_jogador(user_id)
    jogador = database.aplicar_bonus_pet(dict(jogador_base))

    # --- 1. ATAQUE DO JOGADOR ---
    dano_base_player = max(1, jogador['ataque'] - (luta['inimigo_def'] // 2))
    dano_final_player = int(dano_base_player * random.uniform(0.8, 1.2))
    if dano_final_player < 1: dano_final_player = 1 

    luta['inimigo_vida'] -= dano_final_player
    
    # --- VITÓRIA (Checagem imediata) ---
    if luta['inimigo_vida'] <= 0:
        luta['processando'] = False
        await processar_vitoria(query, context, jogador, luta, dano_final_player)
        return

    # --- FEEDBACK INTERMEDIÁRIO (Sem remover botões!) ---
    # Mantemos o reply_markup atual para a tela não pular
    texto_feedback = (
        f"⚔️ Combate\n\n"
        f"👤 Você causou {dano_final_player} de dano!\n"
        f"⏳ O {luta['inimigo_nome']} está preparando um contra-ataque..."
    )
    await query.edit_message_caption(caption=texto_feedback, reply_markup=query.message.reply_markup, parse_mode="Markdown")
    
    await asyncio.sleep(1.2) # Pausa dramática

    # --- 2. TURNO DO MONSTRO ---
    dano_base_monstro = max(1, luta['inimigo_atq'] - (jogador['defesa'] // 2))
    dano_final_monstro = int(dano_base_monstro * random.uniform(0.8, 1.2))
    if dano_final_monstro < 1: dano_final_monstro = 1

    luta['player_vida'] -= dano_final_monstro

    # Sincroniza com o banco
    conn = database.conectar()
    conn.execute("UPDATE personagens SET vida = ? WHERE user_id = ?", (max(0, luta['player_vida']), user_id))
    conn.commit()
    conn.close()

    # --- DERROTA ---
    if luta['player_vida'] <= 0:
        luta['processando'] = False
        texto_derrota = f"💀 DERROTA!\n\nO {luta['inimigo_nome']} causou {dano_final_monstro} de dano e te derrotou!"
        keyboard = [[InlineKeyboardButton("🏰 Voltar", callback_data="ir_0")]]
        context.user_data["luta"] = None
        await query.edit_message_caption(caption=texto_derrota, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # --- FIM DO TURNO ---
    luta['processando'] = False # Destranca
    log = f"👤 Causou {dano_final_player} de dano\n👾 Causou {dano_final_monstro} de dano"
    await voltar_turno_luta(update, context, log)

async def confirmar_cura_luta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cura o jogador e processa o contra-ataque sem remover botões"""
    query = update.callback_query
    user_id = query.from_user.id
    luta = context.user_data.get("luta")
    
    if not luta or luta.get('processando'):
        await query.answer("Aguarde!")
        return

    luta['processando'] = True
    jogador = database.get_jogador(user_id)
    item_escolhido = query.data.split("_")[1]
    
    porcentagens = {"poção pequena": 0.20, "poção média": 0.50, "poção grande": 0.85}
    multiplicador = porcentagens.get(item_escolhido.lower(), 0.20)
    valor_cura = int(jogador['vida_max'] * multiplicador)

    sucesso, mensagem_banco = database.usar_pocao_cura(user_id, item_escolhido, valor_cura)

    if not sucesso:
        luta['processando'] = False
        await query.answer(mensagem_banco, show_alert=True)
        return

    luta['player_vida'] = database.get_jogador(user_id)['vida'] 
    
    texto_feedback = (
        f"💉 Você usou {item_escolhido}!\n"
        f"✨ Recuperou {valor_cura} HP.\n"
        f"⏳ O {luta['inimigo_nome']} aproveitou sua guarda baixa para atacar..."
    )
    # Mantém os botões ativos enquanto espera
    await query.edit_message_caption(caption=texto_feedback, reply_markup=query.message.reply_markup, parse_mode="Markdown")

    await asyncio.sleep(1.2)
    
    # Contra-ataque
    dano_monstro = max(1, luta['inimigo_atq'] - (jogador['defesa'] // 2))
    luta['player_vida'] -= dano_monstro

    conn = database.conectar()
    conn.execute("UPDATE personagens SET vida = ? WHERE user_id = ?", (max(0, luta['player_vida']), user_id))
    conn.commit()
    conn.close()

    luta['processando'] = False
    if luta['player_vida'] <= 0:
        keyboard = [[InlineKeyboardButton("🏰 Voltar", callback_data="ir_0")]]
        context.user_data["luta"] = None
        await query.edit_message_caption(caption=f"💀 O {luta['inimigo_nome']} te nocauteou!", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await voltar_turno_luta(update, context, f"🧪 Curou {valor_cura} HP\n👾 Recebeu {dano_monstro} de dano")
        
        
async def processar_vitoria(query, context, jogador, luta, dano_final):
    """Função auxiliar para limpar a lógica de vitória"""
    user_id = query.from_user.id
    novo_xp = jogador['xp'] + luta['inimigo_xp']
    novo_gold = jogador['gold'] + luta['inimigo_gold']
            
    item_dropado = database.get_drop_aleatorio(luta['mapa_id'])
    mensagem_drop = f"🎁 Drop: {item_dropado}\n" if item_dropado else ""
    
    if item_dropado:
        tipo = "consumivel" if "Poção" in item_dropado or "Maçã" in item_dropado else "material"
        database.adicionar_item_inventario(user_id, item_dropado, tipo, 1)

    conn = database.conectar()
    conn.execute("UPDATE personagens SET xp = ?, gold = ?, vida = ? WHERE user_id = ?", 
                 (novo_xp, novo_gold, luta['player_vida'], user_id))
    conn.commit()
    conn.close()

    texto = (
        f"🏆 VITÓRIA!\n\n"
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

    

async def usar_pocao_luta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Menu de seleção de poções
    texto_escolha = "Qual poção deseja usar?"

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
    await query.answer("Vida recuperada!")
    
    user_id = query.from_user.id
    
    # --- NOVIDADE: Cura 100% ao sair da tela de combate ---
    database.curar_personagem_total(user_id)
    
    jogador = database.get_jogador(user_id)
    mapa_id = jogador['mapa_atual']
    
    context.user_data["luta"] = None 

    from handlers.viagem import exibir_mapa
    await exibir_mapa(update, context, mapa_id)


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