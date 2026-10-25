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
| 2 | Força do Bambam | O Bambam adivinha sua palavra filtrando dicionário e frequência de letras |
| 3 | Simulador de Academia | Fadiga, recuperação, sobrecarga progressiva, dieta e lesão por regra |
| 4 | Tamagotchi do Monstro | Estado evolui pelo tempo real desde o último save |
| 5 | Dungeon da Academia | Fases desenhadas à mão, inimigos perseguem com BFS, combate por fórmula |

## Requisitos (Pop!_OS 24.04)

- Node.js 18+ e npm (testado com Node 24)
- Python 3 com PyGObject e GTK 4 (testado com GTK 4.14.5 / PyGObject 3.48.2)
- Bash

```bash
sudo apt update
sudo apt install -y nodejs npm python3-gi python3-gi-cairo gir1.2-gtk-4.0
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
- Dungeon: `W/A/S/D` para mover, `Q` para sair. Combate é automático ao
  entrar na célula do inimigo.
- `Ctrl+D` encerra.

### Gráfico
- Clique nos botões de ação ou use o teclado.
- Na velha, clique na casa.
- Na dungeon, use `W/A/S/D` ou o D-pad.
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
gui/                  # somente interface: processo filho, widgets e save do pet
docs/protocolo.md     # protocolo GUI <-> BIRL
docs/notas-birl.md    # limitações e contornos da linguagem
saves/                # JSON de save (ignorado no git)
run.sh                # inicia modo terminal ou gráfico
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
