# BIRL Arcade

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
| 2 | Força do Bambam | O Bambam adivinha sua palavra filtrando dicionário e frequência de letras |
| 3 | Simulador de Academia | Fadiga, recuperação, sobrecarga progressiva, dieta e lesão por regra |
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
- Força: digite a palavra secreta; o Bambam chuta uma letra por vez.
- Academia: `1` treino pesado, `2` treino leve, `3` cardio, `4` refeição,
  `5` descanso, `0` sair.
- Tamagotchi: `1` treinar, `2` alimentar, `3` whey/vapo, `4` descansar,
  `5` ignorar (murcha mais rápido), `0` sair.
- Dungeon: `W/A/S/D` para mover, `Q` para sair. Combate por turnos: `1` atacar, `2` habilidade, `3` item, `4` fugir. No combate do Toguro, escolha porcentagem de poder (20/50/80/100).
- `Ctrl+D` encerra.

### Gráfico

- Clique nos botões de ação ou use o teclado.
- Na velha, clique na casa.
- Na dungeon, use `W/A/S/D` ou o D-pad para mover, `1`/`2`/`3`/`4` para ações de combate.
- Em diálogos, aperte `Z` ou `Enter` para avançar.
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
  portraits/          # PNGs de retratos (64x64 recomendado)
  audio/              # .ogg/.wav + manifest.txt (ignorados no git)
docs/protocolo.md     # protocolo GUI <-> BIRL
docs/notas-birl.md    # limitações e contornos da linguagem
saves/                # JSON de save (ignorado no git)
run.sh                # inicia modo terminal ou gráfico
run-tests.sh          # testes de regressão
.github/              # templates, labels, CI, dependabot, codeowners
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
ELE QUE A GENTE QUER? T_I == "id_do_inimigo"
  D_INIM_ID = "id_do_inimigo"
  D_INIM_NOME = "NOME DO INIMIGO"
  D_INIM_HP = <vida>
  D_INIM_HP_MAX = <vida maxima>
  D_INIM_DEF = <defesa>
  D_INIM_DADO = <dado de dano>
  D_INIM_XP = <xp concedido>
  D_INIM_LOOT = <loot concedido>
  D_INIM_FALA = "frase do inimigo"
BIRL
```

Os valores são fáceis de ajustar para balanceamento posterior.

## Créditos de arte e áudio

- Retratos: `assets/portraits/<id>.png` (padrão 64x64). Placeholder gerado se o arquivo não existir.
- Áudio: `assets/audio/` (ignorados no git). Fornecidos pelo usuário. Veja `assets/audio/README.md`.
- Nenhuma arte ou áudio de terceiros (anime, jogos, pessoas reais) é usada ou baixada pelo projeto.

Sai de casa codei pra caralho!™
