# Protocolo GUI ↔ BIRL

A interface gráfica (`gui/`) não contém regra de jogo. Ela inicia o programa BIRL como
processo filho e troca mensagens de texto, **uma linha por mensagem**, por stdin/stdout.
O BIRL continua sendo o cérebro: estado, regras, IA e validação.

## Como o processo é iniciado

```bash
BIRL_MODE=gui BIRL_GAME=velha BIRL_TEMPO=0 \
  node node_modules/birl-js/index.js main.birl
```

| Variável | Significado |
|---|---|
| `BIRL_MODE` | `gui` ativa o protocolo; qualquer outro valor (ou ausente) usa o menu de terminal. |
| `BIRL_GAME` | `velha`, `forca`, `academia`, `tamagotchi` ou `dungeon`. |
| `BIRL_TEMPO` | Segundos reais decorridos desde o último save (usado só pelo Tamagotchi; valor inválido vira `0`). |
| `BIRL_SEED` | Semente dos dados da Dungeon (inteiro > 0). Sem ela, usa o relógio. |

A interface abre **um processo por partida**. Quando o jogo termina, o BIRL emite `END` e
encerra; a interface volta ao menu. Isso evita estado sujo entre jogos.

## BIRL → interface

Todas as linhas abaixo são escritas com `fs.writeSync(1, ...)` (síncrono), porque o BIRL
bloqueia em `fs.readSync(0, ...)` e um `console.log` assíncrono poderia ficar preso no buffer.

| Linha | Efeito na interface |
|---|---|
| `TEXT <texto>` | Adiciona uma linha ao log. `TEXT` sozinho = linha vazia. |
| `DATA <CHAVE> <valor>` | Atualiza o estado estruturado da tela. |
| `PROMPT <tipo> <dica>` | Mostra a dica e habilita a entrada; o BIRL fica bloqueado esperando `INPUT`. |
| `END <resultado>` | Fim da partida. A interface mostra o resultado e libera o botão de voltar. |

### Tipos de `PROMPT`

| Tipo | Widget usado |
|---|---|
| `cell` | Grade 3×3 do jogo da velha; envia o índice `0`–`8`. |
| `choice` | Botões montados a partir de `DATA OPCOES`. |
| `move` | D-pad / WASD da dungeon; envia `w`, `a`, `s`, `d` ou `q`. No terminal real, o BIRL lê a tecla sem Enter. |
| `text` | Campo de texto livre (palavra da forca, etc.). |
| `next` | Botão “Continuar” (envia `ok`). |

### Linha `DIALOGO`

| Linha | Efeito na interface |
|---|---|
| `DIALOGO <personagem>|<texto>` | Exibe uma caixa de diálogo com o nome do personagem e o texto. Na GUI, mostra retrato, efeito de digitação e aguarda tecla (Z/Enter) para avançar. No terminal, desenha caixa com moldura ASCII e pequeno retrato. |

A interface → BIRL não envia nada de volta para `DIALOGO`; o BIRL continua a execução após a linha ser exibida.

### Chaves `DATA` conhecidas

| Chave | Exemplo | Usada por |
|---|---|---|
| `TABULEIRO` | `TABULEIRO X.O......` | Velha |
| `VEZ` | `VEZ X` | Velha |
| `NIVEL` | `NIVEL IMPOSSIVEL` | Velha |
| `PADRAO` | `PADRAO B._._.S` | Força |
| `CERTAS` / `ERRADAS` | `CERTAS BIS` | Força |
| `ERROS` / `MAX` | `ERROS 2`, `MAX 6` | Força |
| `DICA` | `DICA 4 LETRAS` | Força |
| `ATRIBUTOS` | `ATRIBUTOS forca=10 shape=10 ...` | Academia |
| `OPCOES` | `OPCOES 1=TREINAR PESADO\|2=COMER` | Qualquer jogo com `choice` |
| `PET` | `PET treino=60 comida=60 vapo=60 hora=3` | Tamagotchi |
| `SAVE` | `SAVE treino=60 comida=60 vapo=60 hora=3` | Tamagotchi (a interface grava o JSON com timestamp) |
| `MAPA` | `MAPA ##########...` | Dungeon (100 caracteres) |
| `HEROI` | `HEROI nome=BAMBAM hp=50 hpmax=50 atk=4 def=3 pump=20 pumpmax=20 fase=1 nivel=1 xp=0 itens=3 x=1 y=1` | Dungeon |
| `INIM` | `INIM nome=FRANGO MUTANTE hp=20 hpmax=20 def=1 dado=6` (`hpmax=0` fora de combate) | Dungeon |
| `ROLAGEM` | `ROLAGEM D20 17` | Dungeon (a interface pode animar o dado) |
| `RETRATO` | `RETRATO frango_mutante` | ID do retrato (`assets/portraits/<id>.png`) usado pela próxima caixa de diálogo |

### Linha `SOM`

| Linha | Efeito na interface |
|---|---|
| `SOM <id>` | Toca o som associado ao `id`. Se o arquivo de áudio não existir, não toca nada e não dá erro. |

Ids iniciais: `hora_do_show` (início do jogo/batalha e habilidade "HORA DO SHOW"), `birl` (golpe forte e crítico), `ajuda_o_maluco` (cura "AJUDA O MALUCO TA DOENTE"), `acerto`, `erro`, `vitoria`, `derrota`.

O manifesto de áudio fica em `assets/audio/manifest.txt` ligando cada `id` ao nome do arquivo. A interface toca o som em segundo plano (não trava o jogo). Tecla `M` muta/desmuta.

Valores compostos usam `chave=valor` separados por espaço; listas usam `|` e `=`:
`DATA OPCOES 1=TREINAR PESADO|2=COMER FRANGO|0=SAIR`.

### Resultados de `END`

| Jogo | Valores |
|---|---|
| Velha | `VOCE`, `BAMBAM`, `EMPATE` |
| Forca | `BAMBAM_GANHOU` (adivinhou a palavra), `BAMBAM_PERDEU` (errou 6 vezes) |
| Academia / Tamagotchi | `SAIU`, `MURCHOU` (Tamagotchi) |
| Dungeon | `VITORIA`, `DERROTA`, `SAIU` |
| Qualquer | `EOF` (a entrada acabou) |

Nada do protocolo (`SOM`, `DIALOGO`, `DATA`...) é impresso no modo terminal: lá o BIRL desenha a
caixa de diálogo em ASCII e fica em silêncio.

## Interface → BIRL

| Linha | Efeito |
|---|---|
| `INPUT <valor>` | Resposta ao `PROMPT` atual. O BIRL remove o prefixo e valida. |
| `QUIT` | Encerra o processo imediatamente (usado ao fechar a janela). |

## Por que linha a linha casa com o BIRL atual

O BIRL não tem `input()`. A função `LE_LINHA` lê **um byte por vez** com
`fs.readSync(0, BUF, POS, 1)` até encontrar `\n`, descarta o `\r` (Enter em CRLF) e só
decodifica o texto em UTF-8 no fim da linha, então acentos chegam inteiros. Portanto:

- cada mensagem da interface precisa terminar em `\n`;
- nada de JSON multilinha nem tamanho variável sem terminador;
- a interface sempre faz `flush` depois de escrever.

## Exemplo de uma partida (velha)

```
BIRL: TEXT   JOGO DA VELHA VS BAMBAM
BIRL: DATA TABULEIRO .........
BIRL: DATA VEZ X
BIRL: PROMPT cell ESCOLHE UMA CASA (0-8)
GUI : INPUT 4
BIRL: DATA TABULEIRO ....X....
BIRL: TEXT   BAMBAM TA PENSANDO...
BIRL: DATA TABULEIRO O...X....
BIRL: PROMPT cell ESCOLHE UMA CASA (0-8)
...
BIRL: END VOCE
```
