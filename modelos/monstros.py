# Aqui vou deixar as informaçõs sobre os todos os monstros do game

import random

pets = [
    {
        "nome": "Falcão filhote",
        "vida": 100,
        "ataque": 15,
        "defesa": 5,
        "agilidade": 20,
        "imagem": "pet_falcao_filhote.png"
    },
    {
        "nome": "Lobo filhote",
        "vida": 120,
        "ataque": 20,
        "defesa": 10,
        "agilidade": 15,
        "imagem": "pet_lobo_filhote.png"
    },
    {
        "nome": "Tartaruga filhote",
        "vida": 150,
        "ataque": 10,
        "defesa": 15,
        "agilidade": 8,
        "imagem": "pet_tartaruga_filhote.png"
    }
]

def sortear_pet():
    return random.choice(pets)

