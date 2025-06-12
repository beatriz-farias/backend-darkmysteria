
RIDDLES = [
    {
        'id': 1,
        'text': "Sou leve como uma pena, mas nem o homem mais forte consegue me segurar por muito tempo. O que sou eu?",
        'answer': "Respiração"
    },
    {
        'id': 2,
        'text': "Tenho cidades, mas não casas; florestas, mas não árvores; e água, mas não peixes. O que sou eu?",
        'answer': "Mapa"
    },
    {
        'id': 3,
        'text': "Devoro tudo: pássaros, feras, árvores, flores; mordo o ferro, o aço; esmago cidades, roo montanhas. O que sou eu?",
        'answer': "Tempo"
    },
    {
        'id': 4,
        'text': "Falo sem boca e ouço sem orelhas. Não tenho corpo, mas ganho vida com o vento. O que sou eu?",
        'answer': "Eco"
    },
    {
        'id': 5,
        'text': "Um homem é encontrado morto no meio do deserto, segurando um palito de fósforo.",
        'answer': "Ele era passageiro de um balão prestes a cair. Os ocupantes tiraram palitos para decidir quem saltaria (quem pegasse o mais curto morreria)."
    },
    {
        'id': 6,
        'text': "Dois irmãos estão em um velório. Um decide se matar no mesmo dia.",
        'answer': "Eram gêmeos siameses. Um morreu, e o outro preferiu suicidar-se a viver separado."
    },
    {
        'id': 7,
        'text': "Um homem entra em um bar e pede um copo d'água. O bartender aponta uma arma para ele. O homem agradece e vai embora.",
        'answer': "O homem tinha soluços. O susto da arma curou-o."
    },
    {
        'id': 8,
        'text': "Uma mulher acorda com barulhos na cozinha, liga a luz, ri e volta a dormir.",
        'answer': "Ela era sonâmbula e havia deixado a torneira aberta. O barulho era da água; riu aliviada por não ser um assaltante."
    },
    {
        'id': 9,
        'text': "Uma pessoa compra um espelho novo, olha para ele e morre de susto.",
        'answer': "Ela era vampira e não sabia. Viu sua falta de reflexo e entrou em pânico."
    },
    {
        'id': 10,
        'text': "Um homem mata o próprio filho ao vê-lo pela janela do hospital.",
        'answer': "Ele era piloto e acidentalmente bombardeou o hospital onde o filho estava."
    },
    {
        'id': 11,
        'text': "Um livro é vendido com uma foto do comprador na última página.",
        'answer': "Era um álbum de fotos personalizado (o comprador não percebeu)."
    },
    {
        'id': 12,
        'text': "Uma mulher morre ao abrir a porta de casa.",
        'answer': "Ela vivia em um submarino e abriu a porta externa por engano."
    },
    {
        'id': 13,
        'text': "Uma pessoa ganha na loteria e morre no mesmo dia.",
        'answer': "Ela tinha câncer terminal."
    },
    {
        'id': 14,
        'text': "Um casal morre abraçado em um quarto trancado, sem marcas de violência.",
        'answer': "Eram peixes em um aquário e o dono esqueceu de alimentá-los."
    },
    {
        'id': 15,
        'text': "Um cadáver é encontrado em um campo totalmente vazio, sem pegadas ao redor.",
        'answer': "O homem caiu de um avião e aterrissou no local."
    },
    {
        'id': 16,
        'text': "Uma mulher entra em um elevador e morre.",
        'answer': "O elevador estava em construção e ela caiu no vão."
    },
    {
        'id': 17,
        'text': "Um homem morre após ler uma mensagem em seu celular.",
        'answer': "Era um motorista que bateu o carro ao ler a mensagem."
    },
    {
        'id': 18,
        'text': "Uma pessoa morre ao atender o telefone.",
        'answer': "O aparelho estava eletrocutado por um curto-circuito."
    },
    {
        'id': 19,
        'text': "No meio de um campo aberto e deserto, uma mulher encontra um objeto brilhante. Ela o pega, sorri aliviada, e alguns segundos depois, morre.",
        'answer': "A mulher era uma paraquedista e o objeto brilhante era o pino de segurança do seu paraquedas, mas já era tarde demais."
    },
    {
        'id': 20,
        'text': "Uma mulher morre no dia em que ganha um prêmio de 'Pessoa Mais Saudável da Cidade'.",
        'answer': "Ela era alérgica ao material do troféu (níquel) e tocou nele sem saber."
    },
    {
        'id': 21,
        'text': "No meio da sala de estar, um homem encontra uma mancha no teto. Ele sorri.",
        'answer': "O homem era um encanador e a mancha no teto significava que ele havia encontrado o vazamento de água."
    },
    {
        'id': 22,
        'text': "Um homem está andando em um caminho. Ele vira uma esquina e vê um rosto conhecido. Ele corre.",
        'answer': "Ele estava brincando de esconde-esconde e o 'rosto conhecido' era a pessoa que estava procurando por ele."
    },
    {
        'id': 23,
        'text': "Uma pessoa cai da janela de um prédio alto e não se machuca.",
        'answer': "A pessoa caiu da janela do térreo."
    },
    {
        'id': 24,
        'text': "Um homem corre para pegar um ônibus. Ele consegue, mas fica triste.",
        'answer': "Ele pegou o ônibus errado."
    }
    # Adicione mais charadas aqui se desejar!
]

def get_riddle_by_id(riddle_id: int):
    for riddle in RIDDLES:
        if riddle['id'] == riddle_id:
            return riddle
    return None # Retorna None se a charada não for encontrada

def get_next_riddle_id(current_riddle_id: int):
    """Retorna o ID da próxima charada, ou None se for a última."""
    current_index = -1
    for i, riddle in enumerate(RIDDLES):
        if riddle['id'] == current_riddle_id:
            current_index = i
            break
    
    if current_index != -1 and current_index + 1 < len(RIDDLES):
        return RIDDLES[current_index + 1]['id']
    return None # Última charada ou não encontrada

def get_first_riddle_id():
    return RIDDLES[0]['id'] if RIDDLES else None