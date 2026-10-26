# BIRL Arcade

![CI](https://github.com/jotaomh/birl-arcade/actions/workflows/ci.yml/badge.svg)

Fliperama de jogos com tema de academia/maromba. O **cérebro é 100% BIRL**
(`birl-js` 1.0.3): estado, regras e IA. A interface gráfica é uma casca fina em
**Python 3 + GTK4** que conversa com o BIRL por stdin/stdout. O modo terminal
continua existindo e usa exatamente a mesma lógica.

```
  ##########################################
  #                                        #
  #           B I R L   A R C A D E        #
  #      AQUI NAO TEM AGUA COM MUSCULO     #
  #                                        #
  ##########################################
```

## Jogos

| # | Jogo | Inteligência / regra |
|---|------|----------------------|
| 1 | Jogo da Velha vs Bambam | Minimax com níveis de profundidade (impossível no nível 3) |
| 2 | Força do Bambam | O Bambam adivinha sua palavra filtrando dicionário e frequência de letras. Escolhe sempre a letra mais comum entre as palavras que ainda cabem e elimina palavras com letras já erradas. Palavra secreta validada (2-15 letras, A-Z). Dicionário com 250+ palavras em português (tema academia e dia a dia). |
| 3 | Simulador de Academia | Fadiga, recuperação, sobrecarga progressiva, dieta (calorias e proteína gastam por dia) e lesão por regra |
| 4 | Tamagotchi do Monstro | Estado evolui pelo tempo real desde o último save |
| 5 | Dungeon da Academia RPG | Fases desenhadas à mão, inimigos perseguem com BFS, combate por turnos com d20, personagens jogáveis, progressão XP/nível |

## Requisitos (Pop!_OS 24.04)

- Node.js 18+ e npm (testado com Node 24)
- Python 3 com PyGObject e GTK 4 (testado com GTK 4.14.5 / PyGObject 3.48.2)
- Bash

```bash
sudo apt update
sudo apt install -y nodejs npm python3-gi python3-gi-cairo gir1.2-gtk-4.0 pulseaudio-utils alsa-utils
```

Se o Node do apt estiver velho, use o nvm:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install --lts
```

Dependências do projeto:

```bash
npm install
```

## Como rodar

Modo terminal (padrão):

```bash
./run.sh
# ou
./run.sh --terminal
# ou
npm start
```

Modo gráfico:

```bash
./run.sh --gui
# ou
npm run gui
```

O `run.sh` primeiro executa o `build`, que junta os arquivos de `birl/` em
`main.birl`, e depois inicia o modo escolhido.

Para ver o JavaScript gerado pelo transpilador:

```bash
npm run ver-js
```

## Controles

### Terminal
- Digite a opção e aperte **Enter**.
- Velha: escolha uma casa de `0` a `8`.
- Força: digite a palavra secreta (2-15 letras, A-Z, sem acentos); o Bambam chuta letras por frequência, eliminando palavras impossíveis.
- Academia: `1` treino pesado, `2` treino leve, `3` cardio, `4` refeição,
  `5` descanso, `0` sair.
- Tamagotchi: `1` treinar, `2` alimentar, `3` whey/vapo, `4` descansar,
  `5` ignorar (murcha mais rápido), `0` sair.
- Dungeon: `W/A/S/D` move **na hora, sem Enter** (em terminal de verdade; se a entrada for um pipe/arquivo, vale a linha + Enter). `Q` sai e `Ctrl+C` também. Combate por turnos: `1` atacar, `2` habilidade, `3` item (whey), `4` fugir (teste de d20). No ataque do Toguro, escolha a porcentagem de poder (20/50/80/100).
- `Ctrl+D` encerra.

### Gráfico

- Clique nos botões de ação ou use o teclado.
- Na velha, clique na casa.
- Na dungeon, use `W/A/S/D`, as setas ou o D-pad para mover. Nas escolhas (combate, habilidades, personagem) os botões também respondem às teclas `1`-`5`.
- Em diálogos (caixa embaixo da tela, com retrato), aperte `Z`, `Enter` ou `Espaço` para avançar; as outras teclas continuam funcionando.
- `M` para mutar/desmutar o áudio.
- O botão **< Menu** encerra o processo BIRL daquela partida.

## Estrutura

```
birl/                 # fontes BIRL (um arquivo por jogo + núcleo + menu)
  00_core.birl        # protocolo, leitura/escrita, menu e despacho
  10_velha.birl
  20_forca.birl
  30_academia.birl
  40_tamagotchi.birl
  50_dungeon.birl
build                 # junta birl/*.birl em main.birl (HORA DO SHOW + RODA + BIRL)
main.birl             # GERADO pelo build; versionado para rodar sem build
gui/                  # somente interface: processo filho, widgets, dialogos e audio
assets/               # retratos (portraits/) e audio (ignorados no git)
  portraits/          # PNGs de retratos (96x96 recomendado) + README
  audio/              # .ogg/.wav + manifest.txt
docs/protocolo.md     # protocolo GUI <-> BIRL
docs/notas-birl.md    # limitações e contornos da linguagem
saves/                # JSON de save (ignorado no git)
run.sh                # inicia modo terminal ou gráfico
run-tests.sh          # testes de regressão
tests/                # testes que jogam de verdade (mesmo protocolo da GUI)
tools/                # validar_assets.py: confere retratos e áudios
```

### Por que `main.birl` é gerado e versionado?

O BIRL não tem `import` nem módulos: todo programa precisa começar com
`HORA DO SHOW` e terminar com `BIRL`. Para manter os jogos separados no
desenvolvimento, `build` concatena `birl/*.birl` na ordem numérica e adiciona
o cabeçalho e a chamada final. O `main.birl` gerado fica versionado para que
`npx birl main.birl` funcione sem rodar o build; se você editar `birl/`, rode
`./build` antes de testar.

### Regra de arquitetura

- **BIRL**: estado, regras, validação, IA (minimax, filtragem de dicionário,
  BFS), cálculos de tempo e combate.
- **Python/GTK4**: desenhar janela, coletar cliques/teclas, executar o BIRL
  como processo filho e traduzir o protocolo de linhas. Nenhuma regra de jogo.
- **Bash**: `build` e `run.sh`.
- **JSON**: apenas o save do Tamagotchi, gravado pela interface com timestamp.

## Limitações do BIRL (resumo)

- Sem `import`/módulos e sem comentários (`//` quebra o parser).
- `>=` e `<=` têm bug: use `>` e `<`.
- Sem precedência de operadores: tudo é avaliado da esquerda para a direita.
- Condições não aceitam chamada de função nem acesso a membro direto.
- Métodos em literais (`"abc".split("")`) não compilam; atribua antes.
- `0 + string` concatena `"0"`; use `|| ""` para strings e `|| 0` para números.
- Arrays não aceitam índice; use `shift()`/`push()` ou strings com `charAt`.
- `JSON.stringify` com objeto literal não compila; o save é montado por concatenação.

Detalhes e contornos em [`docs/notas-birl.md`](docs/notas-birl.md) e o protocolo
completo em [`docs/protocolo.md`](docs/protocolo.md).

## Personagens jogáveis (Dungeon RPG)

| Personagem | Estilo | Habilidades |
|---|---|---|
| Bambam | Tank (muita HP e força) | BIRL! (golpe forte), AJUDA O MALUCO TA DOENTE (cura), HORA DO SHOW (buff atk) |
| Toguro | Porcentagem de poder | Escolha 20%/50%/80%/100% de força por turno (maior dano = maior custo de Pump e vida) |
| Felipe | Suporte (equilibrado) | Motivação (cura + buff atk), Ficha de Treino (debuff no inimigo) |

## Como adicionar um inimigo

No arquivo `birl/50_dungeon.birl`, na função `D_INIM_CADASTRAR`, adicione um novo bloco:

```
ELE QUE A GENTE QUER? TI == "id_do_inimigo"
  D_INIM_ID = "id_do_inimigo"
  D_INIM_NOME = "NOME DO INIMIGO"
  D_INIM_HP = <vida>
  D_INIM_HP_MAX = <vida maxima>
  D_INIM_DEF = <defesa>
  D_INIM_DADO = <dado de dano, ex.: 8 para d8>
  D_INIM_BONUS = <bonus no d20 de ataque>
  D_INIM_XP = <xp concedido>
  D_INIM_LOOT = <loot concedido>
  D_INIM_FALA = "frase do inimigo"
BIRL
```

Depois, em `D_AGE`, ligue o id à fase (`INIM_ID = "id_do_inimigo"`) e rode `./build`.
Os valores são fáceis de ajustar para balanceamento posterior.

## Testes

```bash
./run-tests.sh          # ou: npm test
```

O script compila, confere que o `main.birl` inicia, compila o Python e roda os testes em
`tests/` (Python `unittest`, sem dependências extras). Eles jogam os cinco jogos pelo protocolo
da interface: a velha impossível nunca perde, a Forca confere o resultado e as letras, a Academia
mantém números inteiros dentro dos limites, o Tamagotchi lida com save corrompido, tempo inválido e
novo dia, e a Dungeon é zerada por um bot com cada personagem.

## Semente dos dados (Dungeon)

Os dados d20 usam um gerador com semente (em BIRL). Para repetir uma partida, defina a semente:

```bash
BIRL_SEED=12345 ./run.sh --terminal
```

Sem `BIRL_SEED`, a semente vem do relógio e cada partida é diferente. Os testes usam sementes fixas.

## Combate (d20)

- **Ataque:** d20 + ATK (+ bônus de precisão do Toguro) contra a defesa do inimigo (10 + DEF). `20` natural é crítico (dano dobrado) e `1` natural é falha crítica.
- **Dano:** d8 + ATK. O inimigo ataca do mesmo jeito: d20 + bônus contra a sua defesa (10 + DEF), dano pelo dado dele.
- **Habilidades** custam Pump e dependem do personagem; o Pump recupera +1 por turno. **Whey** (3 no começo) cura 12 HP. **Fugir** é d20 + DEF contra 12.
- **XP e nível:** cada inimigo derrotado dá XP; subir de nível aumenta vida, Pump e ataque.

## Créditos de arte e áudio

- Retratos: `assets/portraits/<id>.png` (padrão 96x96). Se o arquivo não existir, a caixa de diálogo mostra a inicial do nome. Confira o que falta com `python3 tools/validar_assets.py`.
- Áudio: `assets/audio/`. Fornecido pelo usuário (o som só toca no modo gráfico). Veja `assets/audio/README.md`.
- Nenhuma arte ou áudio de terceiros (anime, jogos, pessoas reais) é usada ou baixada pelo projeto.

Sai de casa codei pra caralho!™

## Contribuição

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para o fluxo de branches, mensagens de
commit (Conventional Commits) e como testar localmente.

A configuração de GitHub (templates de PR/Issue, labels, CI, Dependabot, CODEOWNERS)
fica em [`.github/`](.github/). Abra PRs para a branch `main`; o merge só acontece
após aprovação do mantenedor.

## Proporção de BIRL

O BIRL detém aproximadamente **71,7%** das linhas de código do projeto
(1.826 de 2.545 linhas de código, excluindo `main.birl` gerado e docs). A interface
GTK4/Python responde por ~26,5% e o shell por ~1,7%. O objetivo é manter o BIRL
como protagonista (cérebro), com a GUI como casca fina.
