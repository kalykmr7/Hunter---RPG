import os, random, asyncio, database
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def iniciar_masmorra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia a sequência da Masmorra e configura o Boss do 1º andar."""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Extrai o ID do mapa (ex: entrar_masmorra_1 -> 1)
    try:
        mapa_id = int(query.data.split("_")[-1])
    except:
        await query.answer("Erro ao identificar mapa.")
        return
    
    boss_db = database.get_boss_masmorra(mapa_id, 1)
    if not boss_db:
        await query.answer("Esta masmorra ainda não foi explorada (Sem bosses)...", show_alert=True)
        return

    jogador_base = database.get_jogador(user_id)
    # Aplicamos bônus de Set/Arma/Pet para ter o status real de entrada
    jogador = database.aplicar_bonus_geral(dict(jogador_base))
    
    # CORREÇÃO AQUI: Adicionado (user_id,) no final da execução
    conn = database.conectar()
    pet = conn.execute(
        "SELECT nome, ataque FROM pets_jogador WHERE user_id = ? AND equipado = 1", 
        (user_id,)
    ).fetchone()
    conn.close()

    # Estado inicial da luta em 3 turnos
    context.user_data["luta_masm"] = {
        "andar": 1,
        "boss_nome": boss_db['nome'],
        "boss_hp": boss_db['vida'],
        "boss_max": boss_db['vida'],
        "boss_atq": boss_db['ataque'],
        "boss_def": boss_db['defesa'],
        "player_hp": jogador['vida_max'], # Vida restaurada na entrada
        "player_max": jogador['vida_max'],
        "pet_atq": pet['ataque'] if pet else 0,
        "pet_nome": pet['nome'] if pet else "Pet",
        "mapa_id": mapa_id,
        "processando": False
    }

    await query.answer("👹 Masmorra Iniciada!")
    await renderizar_turno_masmorra(query, context, "🏰 Você entrou nas Ruínas Antigas. Os portões se fecharam atrás de você!")
    

async def renderizar_turno_masmorra(query, context, log=""):
    luta = context.user_data["luta_masm"]
    user_id = query.from_user.id

    texto = (
        f"🏰 Andar {luta['andar']}/3 - Masmorra\n\n"
        f"👹 {luta['boss_nome']}\n"
        f"❤️ HP: {luta['boss_hp']}/{luta['boss_max']}\n\n"
        f"👤 Seu Personagem:\n"
        f"❤️ HP: {luta['player_hp']}/{luta['player_max']}\n\n"
        f"📜 {log}"
    )
    
    keyboard = [[InlineKeyboardButton("⚔️ Atacar Sequência", callback_data="atacar_masmorra")]]
    
    # Verifica poções para mostrar o botão
    itens = database.get_inventario(user_id)
    if any("poção" in i['item_nome'].lower() for i in itens):
        keyboard.append([InlineKeyboardButton("🧪 Usar Poção", callback_data="pocao_masmorra")])

    await query.edit_message_caption(caption=texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def atacar_masmorra_loop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    luta = context.user_data.get("luta_masm")

    if not luta or luta['processando']: return
    luta['processando'] = True
    await query.answer()

    jogador = database.aplicar_bonus_geral(database.get_jogador(user_id))

    # --- TURNO 1: JOGADOR ---
    dano_p = max(1, jogador['ataque'] - (luta['boss_def'] // 2))
    luta['boss_hp'] -= dano_p
    await query.edit_message_caption(caption=f"⚔️ Turno Jogador:\nVocê causou {dano_p} de dano!")
    await asyncio.sleep(1.2)

    if luta['boss_hp'] > 0 and luta['pet_atq'] > 0:
        # --- TURNO 2: PET ---
        dano_pet = max(1, luta['pet_atq'] - (luta['boss_def'] // 3))
        luta['boss_hp'] -= dano_pet
        await query.edit_message_caption(caption=f"🐾 Turno Pet:\n{luta['pet_nome']} atacou e causou {dano_pet} de dano!")
        await asyncio.sleep(1.2)

    # Verifica vitória do andar
    if luta['boss_hp'] <= 0:
        await ganhar_andar(query, context)
        return

    # --- TURNO 3: MONSTRO ---
    dano_m = max(1, luta['boss_atq'] - (jogador['defesa'] // 2))
    luta['player_hp'] -= dano_m
    
    # Sincroniza HP no banco
    conn = database.conectar()
    conn.execute("UPDATE personagens SET vida = ? WHERE user_id = ?", (max(0, luta['player_hp']), user_id))
    conn.commit()
    conn.close()

    if luta['player_hp'] <= 0:
        luta['processando'] = False
        await query.edit_message_caption(
            caption="💀 Você morreu na Masmorra!", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Renascer na Vila", callback_data="ir_0")]])
        )
        return

    luta['processando'] = False
    await renderizar_turno_masmorra(query, context, f"👹 {luta['boss_nome']} te atacou ({dano_m} dano)!")

async def usar_pocao_masmorra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o menu de seleção de poções dentro da masmorra."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🧪 Poção Pequena", callback_data="itemmasm_Poção pequena")],
        [InlineKeyboardButton("⚗️ Poção Média", callback_data="itemmasm_Poção média")],
        [InlineKeyboardButton("🍯 Poção Grande", callback_data="itemmasm_Poção grande")],
        [InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_turno_masm")]
    ]
    
    await query.edit_message_caption(
        caption="Escolha uma poção para recuperar sua vitalidade. Cuidado: O Guardião atacará em seguida!", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def confirmar_cura_masmorra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executa a cura e processa o contra-ataque imediato do Boss."""
    query = update.callback_query
    user_id = query.from_user.id
    luta = context.user_data.get("luta_masm")
    
    if not luta: return
    
    item_nome = query.data.split("_")[1] # Pega "Poção grande", por exemplo.

    jogador_b = database.get_jogador(user_id)
    jogador = database.aplicar_bonus_geral(dict(jogador_b))

    # Adicionado 85% para poção grande aqui:
    porcentagens = {
        "poção pequena": 0.20, 
        "poção média": 0.50, 
        "poção grande": 0.85
    }
    
    multiplicador = porcentagens.get(item_nome.lower(), 0.20)
    cura_total = int(jogador['vida_max'] * multiplicador)

    # Tenta usar a poção via database (isso consome o item e cura o banco)
    sucesso, msg = database.usar_pocao_cura(user_id, item_nome, cura_total)
    
    if not sucesso:
        await query.answer(msg, show_alert=True)
        return

    # Sincroniza a vida na memória da luta após a cura do banco
    luta['player_hp'] = database.get_jogador(user_id)['vida']
    await query.answer(f"Cura aplicada: +{cura_total} HP!")
    
    # TURNO DO BOSS (Gatilha após a poção, pois usar item gasta seu turno)
    dano_boss = max(1, luta['boss_atq'] - (jogador['defesa'] // 2))
    luta['player_hp'] -= dano_boss
    
    # Salva o dano recebido no banco
    conn = database.conectar()
    conn.execute("UPDATE personagens SET vida = ? WHERE user_id = ?", (max(0, luta['player_hp']), user_id))
    conn.commit()
    conn.close()

    if luta['player_hp'] <= 0:
        await query.edit_message_caption(
            caption="💀 Você tentou se curar, mas o golpe do Guardião foi fatal!", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Voltar", callback_data="ir_0")]])
        )
        return

    await renderizar_turno_masmorra(query, context, f"🧪 Usou {item_nome} (+{cura_total} HP)\n👹 Guardião aproveitou e causou {dano_boss} de dano!")

async def renderizar_turno_masmorra_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await renderizar_turno_masmorra(update.callback_query, context, "Próximo round!")

async def ganhar_andar(query, context):
    luta = context.user_data["luta_masm"]
    user_id = query.from_user.id
    mapa_id = luta['mapa_id']
    
    if luta['andar'] < 3:
        luta['andar'] += 1
        prox_boss = database.get_boss_masmorra(mapa_id, luta['andar'])
        
        # Atualiza o dicionário de luta com o próximo boss
        luta['boss_nome'] = prox_boss['nome']
        luta['boss_hp'] = prox_boss['vida']
        luta['boss_max'] = prox_boss['vida']
        luta['boss_atq'] = prox_boss['ataque']
        luta['boss_def'] = prox_boss['defesa']
        luta['processando'] = False
        
        await query.edit_message_caption(
            caption=f"💥 Guardião do Andar {luta['andar']-1} derrotado!", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Entrar no próximo andar", callback_data="voltar_turno_masm")]])
        )
    else:
        boss_f = database.get_boss_masmorra(mapa_id, 3)
        gold = boss_f['gold_recompensa']
        xp = boss_f['xp_recompensa']
        
        # Dar gold via função de admin existente
        from admin import dar_recurso_admin
        dar_recurso_admin(database.buscar_personagem_por_nick(database.get_jogador(user_id)['nick'])['nick'], "gold", gold)
        
        context.user_data["luta_masm"] = None
        await query.edit_message_caption(
            caption=f"🏆 MASMORRA CONCLUÍDA!\n\n💰 Recompensa: {gold} Gold\n✨ Recompensa: {xp} XP", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Sair vitorioso", callback_data=f"ir_{mapa_id}")]])
        )