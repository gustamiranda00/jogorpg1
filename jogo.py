# ============================================================
# O ENIGMA DA MANSÃO ABANDONADA
# Jogo de aventura / escolhas em Python + PyScript
# ============================================================
#
# ESTRUTURA DESTE ARQUIVO
# 1) Compatibilidade do input() com PyScript      -> NÃO ALTERAR
# 2) Funções de acesso ao HTML (imagem/áudio/vídeo/HUD) -> NÃO ALTERAR
# 3) Estado do jogo (vida, inventário, pontuação)
# 4) Motor de cenas (genérico, orientado a dados)
# 5) Conteúdo do jogo: dicionário CENAS
# 6) Funções especiais de decisão (ramificações condicionais)
# 7) Loop principal
#
# Para criar uma cena nova, basta adicionar uma entrada no
# dicionário CENAS lá embaixo. Não é necessário escrever
# funções novas para cenas simples.
# ============================================================

# ------------------------------------------------------------
# 1) ACESSO AO HTML

# ------------------------------------------------------------
from pyscript import document


def definir_titulo(titulo, autor=""):
    document.querySelector("#titulo-jogo").innerText = titulo
    if autor:
        document.querySelector("#autor-jogo").innerText = f"Autor: {autor}"


def mostrar_imagem(caminho):
    img = document.querySelector("#imagem-cena")
    img.src = caminho
    img.style.display = "block"


def esconder_imagem():
    document.querySelector("#imagem-cena").style.display = "none"


def tocar_audio(caminho):
    """
    Troca a trilha sonora de fundo.
    Apenas carrega o áudio (não força play automático,
    pois o navegador só permite tocar som após um clique
    real do usuário). O primeiro play acontece no botão
    INICIAR JOGO do index.html.
    """
    audio = document.querySelector("#audio-fundo")
    audio.src = caminho
    audio.load()
    try:
        audio.play()
    except Exception:
        pass


def parar_audio():
    audio = document.querySelector("#audio-fundo")
    audio.pause()
    audio.currentTime = 0


def tocar_efeito(caminho):
    """Toca um efeito sonoro curto (dano, item, etc.) sem parar a trilha."""
    efeito = document.querySelector("#audio-efeito")
    efeito.src = caminho
    try:
        efeito.play()
    except Exception:
        pass


def mostrar_video(caminho):
    video = document.querySelector("#video-intro")
    video.src = caminho
    video.style.display = "block"
    video.load()


def esconder_video():
    video = document.querySelector("#video-intro")
    video.pause()
    video.style.display = "none"


def atualizar_status():
    """Atualiza o HUD (vida, pontuação e inventário) no topo da página."""
    coracoes = "❤️ " * estado["vida"] + "🖤 " * (VIDA_MAXIMA - estado["vida"])
    document.querySelector("#status-vida").innerText = coracoes.strip()
    document.querySelector("#status-pontuacao").innerText = f"⭐ {estado['pontuacao']} pontos"
    if estado["inventario"]:
        itens = ", ".join(estado["inventario"])
    else:
        itens = "vazio"
    document.querySelector("#status-inventario").innerText = f"🎒 {itens}"


# ------------------------------------------------------------
# 2) ESTADO DO JOGO
# ------------------------------------------------------------
definir_titulo("O ENIGMA DA MANSÃO ABANDONADA", "Feito com PyScript")

VIDA_MAXIMA = 3

estado = {
    "vida": VIDA_MAXIMA,
    "pontuacao": 0,
    "inventario": [],
    "nome": "Investigador",
}


def escolher(mensagem, opcoes_validas):
    """Pede uma opção ao jogador até que ela seja válida."""
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in opcoes_validas:
            return resposta
        print("⚠️  Opção inválida. Digite apenas o número da escolha.")


def aplicar_efeito(efeito):
    """Aplica um efeito de cena: variação de vida, pontos e itens.

    efeito = {
        "vida": -1,
        "pontos": 10,
        "ganhar_item": "chave",
        "perder_item": "lanterna",
        "som": "assets/audios/efeito_dano.wav",
    }
    """
    if not efeito:
        return

    if "vida" in efeito:
        estado["vida"] = max(0, min(VIDA_MAXIMA, estado["vida"] + efeito["vida"]))

    if "pontos" in efeito:
        estado["pontuacao"] += efeito["pontos"]

    if "ganhar_item" in efeito and efeito["ganhar_item"] not in estado["inventario"]:
        estado["inventario"].append(efeito["ganhar_item"])

    if "perder_item" in efeito and efeito["perder_item"] in estado["inventario"]:
        estado["inventario"].remove(efeito["perder_item"])

    if "som" in efeito:
        tocar_efeito(efeito["som"])

    atualizar_status()


# ------------------------------------------------------------
# 3) MOTOR DE CENAS (genérico, orientado a dados)
# ------------------------------------------------------------
def entrar_cena(chave):
    """Processa uma cena do dicionário CENAS e devolve a chave da
    próxima cena a ser exibida."""
    cena = CENAS[chave]

    # --- cena final -------------------------------------------------
    if cena.get("final"):
        aplicar_efeito(cena.get("efeito"))
        if cena.get("imagem"):
            mostrar_imagem(cena["imagem"])
        if cena.get("audio"):
            tocar_audio(cena["audio"])

        print("\n" + "=" * 56)
        print(cena.get("banner", "FIM DE JOGO"))
        print("=" * 56)
        print(cena["texto"].format(**estado))
        print("\n" + "-" * 56)
        print(f"Pontuação final: {estado['pontuacao']} pontos")
        print(f"Itens coletados: {', '.join(estado['inventario']) or 'nenhum'}")
        print("-" * 56)
        print("\nObrigado por jogar! 🎮")
        return None  # encerra o loop principal

    # --- aplica consequências de ENTRAR nesta cena -------------------
    # (é assim que garantimos que a consequência vira uma cena própria,
    # e não um efeito colado na cena anterior)
    aplicar_efeito(cena.get("efeito"))

    # se a vida chegou a zero, a próxima cena mostrada ainda é esta
    # (para o jogador entender o que aconteceu); o game over só
    # acontece depois que ele confirmar a leitura, mais abaixo.

    if cena.get("imagem"):
        mostrar_imagem(cena["imagem"])
    if cena.get("audio"):
        tocar_audio(cena["audio"])

    print("\n" + "=" * 56)
    print(cena["titulo"])
    print("=" * 56)
    print(cena["texto"].format(**estado))

    # --- lógica especial (ramificação condicional) --------------------
    if "logica" in cena:
        proxima = FUNCOES_ESPECIAIS[cena["logica"]]()
        if estado["vida"] <= 0:
            return "fim_ruim"
        return proxima

    # --- opções (filtra as que exigem item que o jogador não tem) -----
    opcoes_disponiveis = []
    for opcao in cena["opcoes"]:
        texto_opcao, destino = opcao[0], opcao[1]
        requisito = opcao[2] if len(opcao) > 2 else None
        if requisito and requisito not in estado["inventario"]:
            continue
        opcoes_disponiveis.append((texto_opcao, destino))

    print()
    for i, (texto_opcao, _destino) in enumerate(opcoes_disponiveis, start=1):
        print(f"{i}) {texto_opcao}")

    numeros_validos = [str(i) for i in range(1, len(opcoes_disponiveis) + 1)]
    escolha = escolher("\nEscolha: ", numeros_validos)
    destino_escolhido = opcoes_disponiveis[int(escolha) - 1][1]

    # game over: se a vida acabou, qualquer caminho leva ao final ruim
    if estado["vida"] <= 0:
        return "fim_ruim"

    return destino_escolhido


# ------------------------------------------------------------
# 4) CONTEÚDO DO JOGO
# ------------------------------------------------------------
CENAS = {

    # ---------------------------------------------------------------
    # PRÓLOGO
    # ---------------------------------------------------------------
    "inicio": {
        "titulo": "A MANSÃO ABANDONADA",
        "imagem": "imagens/inicio.jpg",
        "audio": "assets/audios/trilha_principal.wav",
        "texto": (
            "Você chegou à velha mansão no fim da rua, seguindo um mapa\n"
            "encontrado entre os pertences do seu avô.\n\n"
            "Diz a lenda que, há décadas, um segredo foi escondido em\n"
            "algum lugar dentro daquelas paredes — e que ninguém que\n"
            "entrou depois da meia-noite saiu ileso.\n\n"
            "Você tem {vida} vidas. Cada erro pode custar caro."
        ),
        "opcoes": [
            ("Entrar pela porta da frente", "entrada_porta"),
            ("Entrar pela janela quebrada", "entrada_janela"),
        ],
    },

    "entrada_porta": {
        "titulo": "A PORTA DA FRENTE",
        "imagem": "imagens/entrada_porta.jpg",
        "texto": (
            "A porta range ao ser empurrada. O ar cheira a poeira e\n"
            "madeira velha. Você entra sem chamar atenção."
        ),
        "opcoes": [
            ("Seguir para o corredor principal", "corredor"),
        ],
    },

    "entrada_janela": {
        "titulo": "A JANELA QUEBRADA",
        "imagem": "imagens/entrada_janela.jpg",
        "texto": (
            "Você encontra uma janela com o vidro quebrado nos fundos\n"
            "da casa. Ao vasculhar o parapeito, encontra uma lanterna\n"
            "esquecida — mas os cacos de vidro estão por toda parte."
        ),
        "efeito": {"ganhar_item": "lanterna", "som": "assets/audios/efeito_item.wav"},
        "opcoes": [
            ("Entrar com cuidado mesmo assim", "corte_vidro"),
        ],
    },

    # --- cena de CONSEQUÊNCIA, separada da escolha que a causou -----
    "corte_vidro": {
        "titulo": "UM CORTE NO BRAÇO",
        "imagem": "imagens/corte_vidro.jpg",
        "texto": (
            "Ao passar pela janela, um caco de vidro corta seu braço.\n\n"
            "Você sente uma pontada de dor, mas segue em frente com a\n"
            "lanterna em mãos.\n\n"
            "Você perdeu uma vida."
        ),
        "efeito": {"vida": -1, "som": "assets/audios/efeito_dano.wav"},
        "opcoes": [
            ("Continuar para o corredor principal", "corredor"),
        ],
    },

    # ---------------------------------------------------------------
    # CORREDOR (HUB CENTRAL)
    # ---------------------------------------------------------------
    "corredor": {
        "titulo": "O CORREDOR PRINCIPAL",
        "imagem": "imagens/corredor.jpg",
        "texto": (
            "Você está no corredor principal da mansão. Vários caminhos\n"
            "se abrem diante de você: uma porta trancada, um armário\n"
            "empoeirado, a biblioteca e a escada para o porão.\n\n"
            "Vida: {vida} | Pontos: {pontuacao}"
        ),
        "opcoes": [
            ("Tentar forçar a porta trancada", "porta_falha"),
            ("Vasculhar o armário empoeirado", "armario"),
            ("Ir até a biblioteca", "biblioteca"),
            ("Descer até o porão", "porao_entrada"),
            ("Seguir para o salão principal (encerrar a exploração)", "salao_final"),
        ],
    },

    # --- cena de CONSEQUÊNCIA, separada da tentativa ------------------
    "porta_falha": {
        "titulo": "A PORTA REAGE",
        "imagem": "imagens/porta_falha.jpg",
        "texto": (
            "Você tenta forçar a porta trancada.\n\n"
            "Uma descarga elétrica atravessa sua mão, vinda de algum\n"
            "mecanismo escondido na fechadura.\n\n"
            "Você perdeu uma vida."
        ),
        "efeito": {"vida": -1, "som": "assets/audios/efeito_dano.wav"},
        "opcoes": [
            ("Voltar ao corredor", "corredor"),
        ],
    },

    "armario": {
        "titulo": "O ARMÁRIO EMPOEIRADO",
        "imagem": "imagens/armario.jpg",
        "texto": (
            "Dentro do armário, entre teias de aranha, você encontra\n"
            "uma chave de ferro enferrujada."
        ),
        "efeito": {"ganhar_item": "chave", "pontos": 5, "som": "assets/audios/efeito_item.wav"},
        "opcoes": [
            ("Voltar ao corredor", "corredor"),
        ],
    },

    "biblioteca": {
        "titulo": "A BIBLIOTECA SILENCIOSA",
        "imagem": "imagens/biblioteca.jpg",
        "texto": (
            "Estantes tomam o teto. Sobre uma mesa, um diário antigo\n"
            "aguarda, aberto em uma página sobre 'o guardião do porão'."
        ),
        "efeito": {"ganhar_item": "diario", "pontos": 10, "som": "assets/audios/efeito_item.wav"},
        "opcoes": [
            ("Vasculhar a estante ao fundo", "estante_secreta"),
            ("Voltar ao corredor", "corredor"),
        ],
    },

    "estante_secreta": {
        "titulo": "A ALAVANCA ESCONDIDA",
        "imagem": "imagens/estante_secreta.jpg",
        "texto": (
            "Atrás de alguns livros, seus dedos encontram uma pequena\n"
            "alavanca de metal. Puxá-la pode revelar algo... ou não ser\n"
            "uma boa ideia."
        ),
        "opcoes": [
            ("Puxar a alavanca", "estante_desaba"),
            ("Não arriscar e voltar ao corredor", "corredor"),
        ],
    },

    # --- cena de CONSEQUÊNCIA da alavanca ----------------------------
    "estante_desaba": {
        "titulo": "A ESTANTE DESABA",
        "imagem": "imagens/estante_desaba.jpg",
        "texto": (
            "A alavanca destrava um compartimento secreto, mas também\n"
            "solta a estante inteira sobre você!\n\n"
            "Entre os livros caídos, um medalhão antigo brilha no chão.\n\n"
            "Você perdeu uma vida, mas ganhou o medalhão."
        ),
        "efeito": {
            "vida": -1,
            "pontos": 20,
            "ganhar_item": "medalhao",
            "som": "assets/audios/efeito_dano.wav",
        },
        "opcoes": [
            ("Voltar ao corredor", "corredor"),
        ],
    },

    # ---------------------------------------------------------------
    # PORÃO (exige a chave)
    # ---------------------------------------------------------------
    "porao_entrada": {
        "titulo": "A PORTA DO PORÃO",
        "imagem": "imagens/porao_entrada.jpg",
        "texto": "Uma porta pesada de madeira bloqueia a escada para o porão.",
        "logica": "checar_chave_porao",
    },

    "porao_trancado": {
        "titulo": "TRANCADO",
        "imagem": "imagens/porao_trancado.jpg",
        "texto": (
            "A porta não se move. Você precisa de uma chave para\n"
            "descer até o porão."
        ),
        "opcoes": [
            ("Voltar ao corredor", "corredor"),
        ],
    },

    "porao_aberto": {
        "titulo": "O PORÃO SECRETO",
        "imagem": "imagens/porao_aberto.jpg",
        "audio": "assets/audios/trilha_porao.wav",
        "texto": (
            "A chave gira na fechadura. Uma escada leva a uma câmara\n"
            "de pedra, iluminada por um altar ao centro, onde repousa\n"
            "uma relíquia coberta de símbolos antigos."
        ),
        "opcoes": [
            ("Pegar a relíquia do altar", "relicario_armadilha"),
            ("Não arriscar e voltar ao corredor", "corredor"),
        ],
    },

    # --- cena de CONSEQUÊNCIA de pegar a relíquia --------------------
    "relicario_armadilha": {
        "titulo": "A ARMADILHA DO ALTAR",
        "imagem": "imagens/relicario_armadilha.jpg",
        "texto": (
            "Assim que seus dedos tocam a relíquia, um dardo dispara\n"
            "de uma fenda na parede e atinge seu ombro.\n\n"
            "Mesmo ferido, você consegue guardar a relíquia.\n\n"
            "Você perdeu uma vida, mas ganhou a relíquia."
        ),
        "efeito": {
            "vida": -1,
            "pontos": 30,
            "ganhar_item": "reliquia",
            "som": "assets/audios/efeito_dano.wav",
        },
        "opcoes": [
            ("Voltar ao corredor", "corredor"),
        ],
    },

    # ---------------------------------------------------------------
    # SALÃO FINAL (decide qual final o jogador alcança)
    # ---------------------------------------------------------------
    "salao_final": {
        "titulo": "O SALÃO PRINCIPAL",
        "imagem": "imagens/salao_final.jpg",
        "texto": (
            "Você retorna ao grande salão de entrada. A noite está\n"
            "quase no fim, e é hora de decidir o que fazer com tudo\n"
            "o que encontrou (ou não encontrou) dentro da mansão."
        ),
        "logica": "checar_final",
    },

    # ---------------------------------------------------------------
    # FINAIS (múltiplos finais)
    # ---------------------------------------------------------------
    "fim_bom": {
        "final": True,
        "banner": "🏆 FINAL BOM — O MISTÉRIO REVELADO",
        "imagem": "imagens/fim_bom.jpg",
        "audio": "assets/audios/trilha_final_bom.wav",
        "texto": (
            "Com o diário e a relíquia em mãos, {nome} finalmente\n"
            "entende a história da mansão: a relíquia era a chave para\n"
            "libertar a alma presa que assombrava aquele lugar.\n\n"
            "Você sai pela porta da frente ao amanhecer, deixando para\n"
            "trás uma mansão finalmente em paz."
        ),
    },

    "fim_secreto": {
        "final": True,
        "banner": "✨ FINAL SECRETO — O SEGREDO COMPLETO",
        "imagem": "imagens/fim_secreto.jpg",
        "audio": "assets/audios/trilha_final_bom.wav",
        "texto": (
            "Diário, relíquia e medalhão, juntos, revelam um quarto\n"
            "segredo que ninguém havia encontrado em cem anos: a\n"
            "verdadeira história da família que construiu a mansão.\n\n"
            "{nome} se torna a única pessoa viva a conhecer o segredo\n"
            "completo — e a mansão parece, enfim, agradecer por isso."
        ),
    },

    "fim_neutro": {
        "final": True,
        "banner": "🌫️ FINAL NEUTRO — UMA SAÍDA PARCIAL",
        "imagem": "imagens/fim_neutro.jpg",
        "texto": (
            "Você escapa da mansão com parte da verdade em mãos, mas\n"
            "sente que ainda há perguntas sem resposta.\n\n"
            "Talvez uma segunda visita seja necessária algum dia."
        ),
    },

    "fim_alternativo": {
        "final": True,
        "banner": "🌙 FINAL ALTERNATIVO — DE MÃOS VAZIAS",
        "imagem": "imagens/fim_alternativo.jpg",
        "texto": (
            "Você decide que não vale a pena arriscar mais nada.\n"
            "Sai da mansão de mãos vazias, sem relíquias nem respostas,\n"
            "mas inteiro — e talvez essa seja a vitória possível.\n\n"
            "Algumas lendas é melhor deixar sem final."
        ),
    },

    "fim_ruim": {
        "final": True,
        "banner": "💀 FINAL RUIM — A MANSÃO VENCE",
        "imagem": "imagens/fim_ruim.jpg",
        "audio": "assets/audios/trilha_final_ruim.wav",
        "texto": (
            "Ferimento após ferimento, suas forças finalmente se\n"
            "esgotam. Você desaba no chão empoeirado do corredor.\n\n"
            "A mansão absorve mais uma vítima em silêncio.\n"
            "GAME OVER."
        ),
    },
}


# ------------------------------------------------------------
# 5) FUNÇÕES ESPECIAIS (ramificações condicionais)
# ------------------------------------------------------------
def checar_chave_porao():
    """Decide se o jogador entra no porão ou encontra a porta trancada."""
    if "chave" in estado["inventario"]:
        print("Você usa a chave enferrujada do armário. Ela encaixa perfeitamente.")
        input("\n(pressione ENTER para continuar) ")
        return "porao_aberto"
    print("Você não tem nenhuma chave que sirva nessa fechadura.")
    input("\n(pressione ENTER para continuar) ")
    return "porao_trancado"


def checar_final():
    """Decide qual dos 5 finais o jogador alcança, com base no inventário."""
    inventario = estado["inventario"]
    tem_diario = "diario" in inventario
    tem_reliquia = "reliquia" in inventario
    tem_medalhao = "medalhao" in inventario

    if tem_diario and tem_reliquia and tem_medalhao:
        destino = "fim_secreto"
    elif tem_diario and tem_reliquia:
        destino = "fim_bom"
    elif tem_diario or tem_reliquia or tem_medalhao:
        destino = "fim_neutro"
    else:
        destino = "fim_alternativo"

    print(f"\n(Analisando o que você reuniu: {', '.join(inventario) or 'nada'}...)")
    input("\n(pressione ENTER para descobrir seu final) ")
    return destino


FUNCOES_ESPECIAIS = {
    "checar_chave_porao": checar_chave_porao,
    "checar_final": checar_final,
}


# ------------------------------------------------------------
# 6) LOOP PRINCIPAL
# ------------------------------------------------------------
atualizar_status()
cena_atual = "inicio"

while cena_atual is not None:
    cena_atual = entrar_cena(cena_atual)
