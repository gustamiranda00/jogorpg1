# 🏚️ O Enigma da Mansão Abandonada

Jogo de aventura em **Python + PyScript**, com escolhas, sistema de vida,
inventário, pontuação, cenas de consequência separadas e **5 finais
diferentes**. Roda direto no navegador — sem precisar instalar Python
no computador de quem for jogar.

## 🎮 Jogar agora

Se você já publicou este repositório no GitHub Pages, basta acessar o link
do Pages (Settings → Pages) e clicar em **INICIAR JOGO**.

## 📁 Estrutura do projeto

```
mansao-enigma/
├── index.html          -> página do jogo (HTML + CSS + PyScript)
├── jogo.py              -> todo o motor e o roteiro do jogo
├── mini-coi.js            -> habilita o modo "worker" também no GitHub Pages
├── servidor.py           -> servidor local opcional para testes
├── INICIAR_JOGO.bat      -> atalho para Windows (duplo clique)
├── iniciar_jogo.sh       -> atalho para Linux/Mac
├── assets/
│   ├── imagens/          -> uma imagem por cena (pode trocar pelas suas)
│   └── audios/            -> trilha sonora e efeitos (placeholders)
└── README.md
```

## 🧠 Como o jogo é organizado (`jogo.py`)

O jogo é **orientado a dados**: cada cena é uma entrada no dicionário
`CENAS`, no formato:

```python
"porta_falha": {
    "titulo": "A porta reage",
    "imagem": "imagens/porta_falha.jpg",
    "texto": (
        "Você tenta forçar a porta.\n\n"
        "Uma descarga atravessa sua mão.\n\n"
        "Você perdeu uma vida."
    ),
    "efeito": {"vida": -1, "som": "assets/audios/efeito_dano.wav"},
    "opcoes": [
        ("Voltar", "corredor"),
    ],
},
```

Para criar uma cena nova, basta adicionar uma entrada assim — **não é
necessário escrever uma função nova**. O motor genérico (`entrar_cena`)
cuida de mostrar a imagem, tocar o áudio, aplicar o efeito, imprimir o
texto e perguntar a escolha.

### ⚠️ Consequências são sempre cenas separadas

Seguindo a boa prática pedida no enunciado, **nenhuma escolha aplica um
efeito e pula direto para outra cena no mesmo passo**. O fluxo é sempre:

```
cena da escolha  →  cena de consequência (mostra o que aconteceu)  →  cena seguinte
```

Exemplo real do jogo: `corredor` → (tentar abrir a porta) → `porta_falha`
(cena própria, explicando a descarga elétrica e a perda de vida) → o
jogador clica "Voltar" → `corredor` de novo.

### ❤️ Sistema de vida

- `estado["vida"]` começa em 3 (constante `VIDA_MAXIMA`).
- Toda cena pode ter um `"efeito"` com `"vida": -1` (ou outro valor).
- Se a vida chegar a `0`, o próprio motor redireciona automaticamente
  para o final `fim_ruim` assim que o jogador confirmar a leitura da
  última cena de consequência.

### 🎒 Inventário

- `estado["inventario"]` é uma lista de strings (`"chave"`, `"diario"`...).
- Uma cena pode dar um item (`"ganhar_item": "chave"`) ou exigir um item
  para uma opção aparecer (terceiro elemento da tupla de opção):

```python
"opcoes": [
    ("Abrir com a chave", "porao_aberto", "chave"),  # só aparece com a chave
],
```

- Ramificações mais complexas (como "só entra no porão se tiver a
  chave, senão mostra outra cena") usam uma função especial referenciada
  por `"logica"` (veja `FUNCOES_ESPECIAIS` no final do arquivo).

### ⭐ Pontuação

- `estado["pontuacao"]` aumenta com `"pontos": N` no efeito de qualquer cena.
- A pontuação final aparece na tela de encerramento e no HUD durante o jogo.

### 🏁 Múltiplos finais

Toda cena marcada com `"final": True` é um final. O jogo tem 5:

| Chave              | Como alcançar                                              |
|--------------------|--------------------------------------------------------------|
| `fim_bom`          | Termina com o diário **e** a relíquia                        |
| `fim_secreto`      | Termina com diário **+** relíquia **+** medalhão (o "final verdadeiro", mais difícil) |
| `fim_neutro`       | Termina com apenas um item importante                        |
| `fim_alternativo`  | Termina sem nenhum item (foi direto ao salão final)           |
| `fim_ruim`         | A vida chega a zero em qualquer momento                       |

A escolha do final acontece na função `checar_final()`, chamada pela cena
`salao_final`.

### 🖼️ Imagem, 🎵 áudio e 🎬 vídeo por cena

Funções já prontas em `jogo.py` (não precisam ser alteradas):

```python
mostrar_imagem("imagens/cena.jpg")
esconder_imagem()

tocar_audio("assets/audios/trilha.wav")   # troca a trilha de fundo
parar_audio()
tocar_efeito("assets/audios/efeito.wav")   # efeito curto, sem parar a trilha

mostrar_video("imagens/introducao.mp4")
esconder_video()
```

## 🎨 Sobre os assets incluídos

As imagens (`imagens/*.jpg`) e os áudios (`assets/audios/*.wav`)
deste projeto foram **gerados automaticamente como placeholders**
(imagens com título da cena, áudios com tons sintetizados) só para o
jogo já funcionar "out of the box". Fique à vontade para substituir
todos eles pelas suas próprias artes/músicas — só manter os mesmos
nomes de arquivo (ou atualizar os caminhos correspondentes dentro de
`CENAS`, em `jogo.py`).

## 🧪 Testar localmente

**Opção 1 — com `mini-coi.js` (igual ao GitHub Pages)**, funciona com
qualquer servidor estático simples:

```bash
python -m http.server 8000
```

Depois abra `http://localhost:8000` no navegador. Na primeira vez a
página pode recarregar sozinha (normal, é o `mini-coi.js` se ativando).

**Opção 2 — com o servidor incluso** (mais rápido para testar, já envia
os cabeçalhos de isolamento de origem direto, sem precisar do
`mini-coi.js`/Service Worker):

```bash
python servidor.py
```

ou, no Windows, dando duplo clique em `INICIAR_JOGO.bat`.

> Não abra o `index.html` direto pelo "Abrir arquivo" do navegador
> (`file://...`) — o PyScript precisa de um servidor HTTP, mesmo que
> local, para carregar o `jogo.py` e os assets corretamente.

## 🚀 Publicar no GitHub Pages

1. Crie um repositório no GitHub e envie **todos os arquivos desta pasta**
   (mantendo a estrutura, incluindo a pasta `assets/` e o arquivo
   `mini-coi.js` na raiz).
2. No repositório, vá em **Settings → Pages**.
3. Em **Build and deployment**, escolha **Deploy from a branch**.
4. Selecione a branch `main` e a pasta `/ (root)`.
5. Salve e aguarde alguns minutos. O link ficará disponível na própria
   página de Settings → Pages.
6. Na **primeira vez** que abrir o link, a página pode recarregar
   sozinha uma vez (é o `mini-coi.js` se registrando) — isso é normal,
   só acontece na primeira visita.

### ⚠️ Por que existe o arquivo `mini-coi.js`?

O `input()` do Python, usado nas escolhas do jogo, só funciona quando o
PyScript roda em modo **`worker`** (`<script type="py" ... worker>`).
Esse modo depende de uma tecnologia do navegador (`SharedArrayBuffer`)
que só fica disponível quando o site envia dois cabeçalhos HTTP
especiais (`Cross-Origin-Opener-Policy` e `Cross-Origin-Embedder-Policy`).

O problema é que o **GitHub Pages não permite configurar cabeçalhos HTTP
customizados**. A solução usada aqui é o [`mini-coi.js`](https://github.com/WebReflection/mini-coi)
— um pequeno Service Worker que "finge" esses cabeçalhos no navegador de
quem está jogando, sem precisar de nenhuma configuração no GitHub. Ele já
está incluído no projeto e referenciado no `<head>` do `index.html`;
**não precisa mexer em nada, só manter o arquivo na raiz do repositório.**

## ✏️ Personalizar

- **Trocar o título/autor:** edite a chamada `definir_titulo(...)` no
  topo de `jogo.py`.
- **Adicionar uma cena:** copie um bloco de `CENAS` e ajuste `titulo`,
  `imagem`, `texto`, `efeito` e `opcoes`.
- **Adicionar um novo final:** crie uma entrada com `"final": True` e
  aponte para ela dentro de `checar_final()` (ou de qualquer outra
  lógica que você criar).
- **Cores/visual:** o CSS está todo dentro do `<style>` do `index.html`.

---

Feito com 🐍 Python + PyScript.
