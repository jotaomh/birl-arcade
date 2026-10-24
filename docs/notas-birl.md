# Notas do BIRL (birl-js 1.0.3)

Descobertas feitas testando o transpilador de verdade. Nada aqui é invenção de sintaxe.

## Gramática / parser

- Comentários (`//`, `#`) quebram o parser. O `build` não gera comentários.
- `>=` e `<=` não compilam; use `>` e `<` com variáveis temporárias.
- **Não há precedência de operadores**: `A + B * C` é avaliado como `(A + B) * C`.
  Sempre quebre cálculos em variáveis.
- Condições de `ELE QUE A GENTE QUER?` e `NEGATIVA BAMBAM (...)` **não aceitam**:
  - chamada de função: `ELE ... FS.existsSync(x)` falha; faça `FRANGO EX = ... EXISTS(x)` antes;
  - acesso a membro: `ELE ... A.length > 0` falha; faça `FRANGO N = 0 + A.length` antes.
- Chamada de método em **literal** falha: `"abc".split("")` não compila. Atribua a uma
  variável primeiro e chame `S.split("")`.
- `BORA CUMPADI` não aceita chamada de função nem expressão começando por literal.
  Atribua a uma variável e retorne a variável.
- Funções exigem pelo menos 1 parâmetro.

## Números, strings e arrays

- `0 + string` **concatena** `"0"` na frente. Use:
  - número/array: `... || 0`;
  - string: `... || ""`.
- Array vazio `[]` quebra; índice `A[i]` não existe.
- Para percorrer arrays com segurança use `shift()` + `push()` e `length` em variável.
  Isso viabiliza filas de BFS e listas de candidatos da forca.
- Strings aceitam `charAt`, `substring`, `indexOf`, `split`, `join`, `replace`,
  `toUpperCase`, `repeat`, `splice` (em array).
- `String.fromCharCode(65)` funciona e devolve string.
- `JSON.parse` funciona e o resultado aceita acesso a membro (`O.treino`).
  `JSON.stringify` com objeto literal **não** compila; JSON de save é montado por
  concatenação de string.

## I/O

- Não existe `input()`. Leitura: `fs.readSync(0, BUF, 0, 1)` (sem o 5º argumento,
  que causa `ESPIPE` em pipe).
- `console.log` é assíncrono em pipe. Para o protocolo da GUI use
  `fs.writeSync(1, texto + "\n")`, que é síncrono e não trava enquanto o processo
  está bloqueado lendo stdin.
- `process.env`, `process.exit` e `Date.now()` funcionam.
- `fs.existsSync`, `fs.readFileSync`, `fs.writeFileSync` funcionam.

## Recursão

- Recursão de funções funciona (usada no minimax). Profundidade 9 é tranquila.
