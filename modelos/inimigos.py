# Aqui ficam os monstos a serem caçados.


# Dicionário de inimigos organizados por ID de MAPA
# Isso torna a busca muito mais rápida para o bot
inimigos_por_mapa = {
    1: [ # Acampamento do Pioneiro
        {"nome": "Barata", "vida": 30, "atq": 5, "def": 2, "xp": 15, "gold": 10, "img": "barata.png"},
        {"nome": "Aranha", "vida": 45, "atq": 8, "def": 3, "xp": 25, "gold": 20, "img": "aranha.png"},
        {"nome": "Centopéia", "vida": 30, "atq": 5, "def": 1, "xp": 15, "gold": 10, "img": "centopeia.png"},
        {"nome": "Grilo", "vida": 30, "atq": 5, "def": 0, "xp": 15, "gold": 10, "img": "grilo.png"},
        {"nome": "Borboleta", "vida": 30, "atq": 5, "def": 0, "xp": 15, "gold": 10, "img": "borboleta.png"},
    ],

    2: [ # Bosque Queimado
        {"nome": "Esqueleto Carbonizado", "vida": 65, "atq": 12, "xp": 40, "gold": 35, "img": "esqueleto.png"},
        {"nome": "Aranha das Cinzas", "vida": 55, "atq": 15, "xp": 45, "gold": 40, "img": "aranha.png"},
    ],
    # Você pode ir adicionando conforme cria os novos mapas...
}