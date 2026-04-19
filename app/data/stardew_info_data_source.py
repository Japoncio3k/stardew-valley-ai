import random

MOCK_DATA = [
    {
        "category": "personagem",
        "name": "Penny",
        "description": (
            "Penny é uma moradora de Pelican Town que vive com sua mãe Pam. "
            "Ela adora ensinar as crianças da vila e sonha em ter uma família. "
            "Seus itens favoritos incluem Melon, Poppy e Red Plate."
        ),
    },
    {
        "category": "personagem",
        "name": "Abigail",
        "description": (
            "Abigail é filha de Pierre e Caroline. Ela é aventureira e ama "
            "explorar as minas. Seus itens favoritos são Amethyst, Chocolate Cake e Pufferfish."
        ),
    },
    {
        "category": "personagem",
        "name": "Harvey",
        "description": (
            "Harvey é o médico de Pelican Town. Ele é tímido mas gentil. "
            "Seus itens favoritos incluem Coffee, Pickles e Wine."
        ),
    },
    {
        "category": "personagem",
        "name": "Sebastian",
        "description": (
            "Sebastian é um programador solitário que vive no porão da casa de sua mãe. "
            "Ele gosta de motocicletas e ficção científica. Itens favoritos: Frozen Tear, Obsidian e Pumpkin Soup."
        ),
    },
    {
        "category": "cultivo",
        "name": "Morango (Strawberry)",
        "description": (
            "Morango é um cultivo de primavera que cresce em 8 dias. "
            "Após a primeira colheita, produz novamente a cada 4 dias. "
            "Vende por 120g e é excelente para lucro no primeiro ano."
        ),
    },
    {
        "category": "cultivo",
        "name": "Abóbora (Pumpkin)",
        "description": (
            "A Abóbora é um cultivo de outono que cresce em 13 dias. "
            "Vende por 320g e pode se tornar um vegetal gigante. "
            "É o item favorito de vários moradores."
        ),
    },
    {
        "category": "cultivo",
        "name": "Melão (Melon)",
        "description": (
            "O Melão é um cultivo de verão que cresce em 12 dias. "
            "Vende por 250g e pode crescer em tamanho gigante se plantado em blocos de 3x3. "
            "É necessário para o bundle de verão no Community Center."
        ),
    },
    {
        "category": "pesca",
        "name": "Pufferfish",
        "description": (
            "O Pufferfish é um peixe raro encontrado no oceano durante o verão, "
            "preferencialmente em dias ensolarados. Vende por 200g e é o item favorito de Abigail."
        ),
    },
    {
        "category": "pesca",
        "name": "Legend",
        "description": (
            "O Legend é o peixe mais raro do jogo. Só pode ser pescado no lago da montanha "
            "durante a primavera em dias chuvosos, usando isca. Vende por 5.000g."
        ),
    },
    {
        "category": "minas",
        "name": "Andar 100 das minas",
        "description": (
            "O andar 100 das minas é o mais profundo e contém inimigos poderosos. "
            "A partir deste ponto o jogador acessa as Minas do Crânio (Skull Cavern) no deserto. "
            "Iridium Ore pode ser encontrado em abundância na Skull Cavern."
        ),
    },
    {
        "category": "minas",
        "name": "Iridium Ore",
        "description": (
            "Iridium Ore é o minério mais valioso do jogo, encontrado principalmente "
            "na Skull Cavern. É usado para criar ferramentas de iridium, que são as mais poderosas. "
            "Também pode ser obtido de cofres e inimigos raros."
        ),
    },
    {
        "category": "fazenda",
        "name": "Celeiro (Barn)",
        "description": (
            "O Celeiro abriga animais como vacas, cabras, ovelhas e porcos. "
            "No nível máximo (Big Barn) comporta até 12 animais e libera a criação de porcos, "
            "que encontram trufas automaticamente."
        ),
    },
    {
        "category": "fazenda",
        "name": "Sprinkler de Iridium",
        "description": (
            "O Sprinkler de Iridium irriga automaticamente 24 casas ao redor dele "
            "em formato 5x5. É o sprinkler mais eficiente do jogo e elimina a necessidade "
            "de regar plantas manualmente."
        ),
    },
]


class StardewDatasource:
    def get(self, query: str) -> dict[str, str]:
        query_lower = query.lower()

        matches = [item for item in MOCK_DATA if item["category"] in query_lower or item["name"].lower() in query_lower]

        if matches:
            return random.choice(matches)

        return random.choice(MOCK_DATA)
