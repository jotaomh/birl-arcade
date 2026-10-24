# BIRL Arcade

Fliperama de jogos de terminal escrito na linguagem **BIRL** (`birl-js`), com tema de academia/maromba.
Sem servidor web, sem interface gráfica, sem água com músculo: tudo roda no terminal.

```
  ##########################################
  #                                        #
  #           B I R L   A R C A D E        #
  #      AQUI NAO TEM AGUA COM MUSCULO     #
  #                                        #
  ##########################################
```

## Jogos

| # | Jogo | Status |
|---|------|--------|
| 1 | Jogo da Velha vs Bambam | pronto |
| 2 | Simulador de Academia (RPG de texto) | em breve |
| 3 | Tamagotchi do Monstro | em breve |
| 4 | Dungeon da Academia (roguelike ASCII) | em breve |

Ao terminar qualquer jogo, o jogo volta para o menu principal.

## Requisitos

- Node.js 18+ (testado no Node 24)
- npm
- Pop!_OS / Ubuntu (ou qualquer Linux com terminal)

## Instalação (Pop!_OS)

```bash
sudo apt update
sudo apt install -y nodejs npm
```

Se o Node do apt estiver muito velho, use o nvm:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install --lts
```

Depois, no diretório do projeto:

```bash
npm install
```

## Como rodar

```bash
npm start
```

ou diretamente:

```bash
npx birl main.birl
```

Para ver o JavaScript gerado pelo transpilador:

```bash
npx birl -j main.birl
```

## Controles

- Digite o número da opção e aperte **Enter**.
- No jogo da velha, escolha uma casa de `0` a `8` (a posição aparece no tabuleiro).
- `Ctrl+D` (fim da entrada) encerra o fliperama.

## Estrutura

```
main.birl        # menu + todos os jogos (100% da lógica)
package.json     # apenas metadados e scripts npm
README.md
```

### Por que tudo em um único `main.birl`?

A linguagem BIRL (`birl-js` 1.0.3) **não possui `import`, `require` de outros arquivos `.birl` nem
módulos**. Cada programa precisa começar com `HORA DO SHOW` e terminar com `BIRL`, e o
transpilador gera um único script JavaScript. Por isso cada jogo é uma função dentro de
`main.birl`, o que mantém 100% da lógica em BIRL. Se no futuro a linguagem ganhar módulos,
os blocos já estão separados por funções e podem ser movidos para arquivos próprios.

## Curiosidades da linguagem (descobertas na prática)

- Variáveis: `FRANGO nome = "valor"` (tipos são só água com músculo).
- Imprimir: `CE QUER VER ESSA PORRA?(...)`.
- Se: `ELE QUE A GENTE QUER? condicao ... BIRL` (sem parênteses na condição!).
- Senão: `NAO VAI DAR NAO ... BIRL`; senão-se: `QUE NAO VAI DAR O QUE? cond ...`.
- Laço: `NEGATIVA BAMBAM (condicao) ... BIRL`.
- Funções: `OH O HOME AI PO TIPO NOME(TIPO A) ... BORA CUMPADI A BIRL` — **precisa de pelo menos 1 parâmetro**.
- Chamar função: `AJUDA O MALUCO TA DOENTE NOME(1)`.
- Números aleatórios: `Math.random()` / `Math.floor(...)` (via JS), com auxílio de `|| 0`.
- Leitura de teclado: `fs.readSync(0, ...)` byte a byte (a linguagem não tem `input()`).
- Sem comentários (`//` quebra o parser) e `>=` / `<=` têm bug na gramática: use `>` / `<`.

Sai de casa codei pra caralho!™
