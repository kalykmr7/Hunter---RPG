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
    mapa_id = jogador['mapa_atual']

    # 2. Sorteia o inimigo
    lista_possivel = inimigos_por_mapa.get(mapa_id, [])
    if not lista_possivel:
        await query.answer("Nenhum monstro nesta área...")
        return

    inimigo = random.choice(lista_possivel).copy() # .copy() para não alterar o original

    # 3. SALVA O ESTADO DA LUTA (Importante para os turnos)
    context.user_data["luta"] = {
        "inimigo_nome": inimigo['nome'],
        "inimigo_vida": inimigo['vida'],
        "inimigo_vida_max": inimigo['vida'],
        "inimigo_atq": inimigo['atq'],
        "inimigo_def": inimigo.get('def', 0), # Evita erro se não tiver defesa
        "inimigo_xp": inimigo['xp'],
        "inimigo_gold": inimigo['gold'],
        "inimigo_img": inimigo['img'],
        "player_vida": jogador['vida'],
        "mapa_id": mapa_id
    }

    # 4. Interface Inicial do Encontro
    texto = (
        f"⚔️ **UM INIMIGO APARECEU!**\n\n"
        f"👾 Inimigo: {inimigo['nome']}\n"
        f"❤️ Vida: {inimigo['vida']}/{inimigo['vida']}\n\n"
        f"O que você vai fazer?"
    )

    keyboard = [
        [InlineKeyboardButton("⚔️ ATACAR", callback_data="atacar_turno")],
        [InlineKeyboardButton("🏃 FUGIR", callback_data="fugir_luta")]
    ]
    
    caminho_img = os.path.join("imagens", inimigo['img'])
    
    try:
        with open(caminho_img, "rb") as foto:
            await query.edit_message_media(
                media=InputMediaPhoto(media=foto, caption=texto, parse_mode="Markdown"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def atacar_turno(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    luta = context.user_data.get("luta")
    
    if not luta:
        await query.edit_message_caption("❌ Erro: Luta não encontrada.")
        return

    jogador = database.get_jogador(user_id)

    # --- ETAPA 1: SEU ATAQUE ---
    dano_player = max(1, jogador['ataque'] - (luta['inimigo_def'] // 2))
    luta['inimigo_vida'] -= dano_player
    
    texto_combate = (
        f"⚔️ **COMBATE EM ANDAMENTO**\n\n"
        f"👤 Você atacou o {luta['inimigo_nome']}!\n"
        f"💥 Causou {dano_player} de dano.\n\n"
        f"👾 {luta['inimigo_nome']}: ❤️ {max(0, luta['inimigo_vida'])}/{luta['inimigo_vida_max']}\n"
        f"👤 Você: ❤️ {luta['player_vida']}/{jogador['vida']}\n\n"
        f"⏳ Aguardando turno do inimigo..."
    )

    # Remove os botões para evitar cliques repetidos durante o delay
    await query.edit_message_caption(caption=texto_combate, reply_markup=None, parse_mode="Markdown")

    # --- ETAPA 2: CHECAGEM DE VITÓRIA ---
    if luta['inimigo_vida'] <= 0:
        await asyncio.sleep(1) 
        
        novo_xp = jogador['xp'] + luta['inimigo_xp']
        novo_gold = jogador['gold'] + luta['inimigo_gold']
        
        # Salva o progresso
        conn = database.conectar()
        conn.execute("UPDATE personagens SET xp = ?, gold = ? WHERE user_id = ?", (novo_xp, novo_gold, user_id))
        conn.commit()
        conn.close()

        texto_resultado = (
            f"🏆 **VITÓRIA!**\n\n"
            f"Você derrotou o {luta['inimigo_nome']}!\n"
            f"💰 +{luta['inimigo_gold']} Gold | ✨ +{luta['inimigo_xp']} XP\n"
        )

        # Logica de Level Up
        if novo_xp >= 100:
            status_novos = database.subir_de_nivel(user_id)
            if status_novos:
                texto_resultado += (
                    f"\n🌟 **LEVEL UP!** 🌟\n"
                    f"Você agora é nível {status_novos['level']}!\n"
                    f"❤️ Vida Max: {status_novos['vida']}\n"
                    f"⚔️ Ataque: {status_novos['ataque']} | 🛡️ Defesa: {status_novos['defesa']}\n"
                )

        keyboard = [[InlineKeyboardButton("🏃 Voltar ao Mapa", callback_data=f"ir_{luta['mapa_id']}")]]
        context.user_data["luta"] = None
        await query.edit_message_caption(caption=texto_resultado, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # --- ETAPA 3: TURNO DO MONSTRO (DELAY) ---
    await asyncio.sleep(1.5) 

    dano_monstro = max(1, luta['inimigo_atq'] - (jogador['defesa'] // 2))
    luta['player_vida'] -= dano_monstro

    # --- ETAPA 4: CHECAGEM DE DERROTA ---
    if luta['player_vida'] <= 0:
        texto_derrota = (
            f"💀 **DERROTA!**\n\n"
            f"O {luta['inimigo_nome']} te nocauteou com um ataque de {dano_monstro}!\n"
            f"Você fugiu para a vila para se recuperar."
        )
        # Ao morrer, o jogador volta para a Vila (Mapa 0)
        keyboard = [[InlineKeyboardButton("🏰 Voltar para a Vila", callback_data="ir_0")]]
        context.user_data["luta"] = None
        await query.edit_message_caption(caption=texto_derrota, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # --- ETAPA 5: CONTINUAÇÃO DA LUTA ---
    texto_proximo_turno = (
        f"⚔️ **COMBATE EM ANDAMENTO**\n\n"
        f"👾 {luta['inimigo_nome']} contra-atacou!\n"
        f"💥 Você sofreu {dano_monstro} de dano.\n\n"
        f"👾 {luta['inimigo_nome']}: ❤️ {luta['inimigo_vida']}/{luta['inimigo_vida_max']}\n"
        f"👤 Você: ❤️ {luta['player_vida']}/{jogador['vida']}\n\n"
        f"Sua vez! O que vai fazer?"
    )
    
    keyboard = [
        [InlineKeyboardButton("⚔️ ATACAR", callback_data="atacar_turno")],
        [InlineKeyboardButton("🏃 FUGIR", callback_data="fugir_luta")]
    ]
    
    await query.edit_message_caption(caption=texto_proximo_turno, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def voltar_ao_mapa(update, context):
    query = update.callback_query
    await query.answer("Você fugiu da luta!")
    
    user_id = query.from_user.id
    jogador = database.get_jogador(user_id)
    mapa_id = jogador['mapa_atual']
    
    context.user_data["luta"] = None # Limpa a luta ao fugir

    from handlers.viagem import exibir_mapa
    await exibir_mapa(update, context, mapa_id)