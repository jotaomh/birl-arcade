# Contribuindo com o BIRL Arcade

Obrigado por querer contribuir! Este é um fliperama de jogos em **BIRL** com interface **GTK4/Python**. O cérebro (regras, estado, IA) vive 100% em BIRL; o Python é só a casca gráfica.

## Fluxo de branches

1. A branch padrão é `main` (ex-`master`). Nunca faça commit direto nela.
2. Crie uma branch descritiva a partir de `main`:
   - `chore/...` — manutenção, build, CI, docs
   - `feature/...` — nova funcionalidade (ex.: `feature/dungeon-rpg`)
   - `fix/...` — correção de bug
3. Faça commits pequenos e claros, no estilo [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: ...`
   - `fix: ...`
   - `chore: ...`
   - `docs: ...`
4. Dê push da branch e abra um Pull Request para `main`.
5. Só faça merge do PR para `main` após aprovação do mantenedor.

## Como testar

```bash
# 1. Dependências (Pop!_OS 24.04)
sudo apt update
sudo apt install -y nodejs npm python3-gi python3-gi-cairo gir1.2-gtk-4.0
npm install

# 2. Modo terminal (padrão)
./run.sh

# 3. Modo gráfico (GTK4)
./run.sh --gui

# 4. Compilar o BIRL
./build
```

## Regras do BIRL (respeite ao editar `birl/`)

- Sem `import`/módulos: tudo fica num único `main.birl` (de `HORA DO SHOW` até `BIRL`), gerado pelo `build`.
- Sem comentários (`//` quebra o parser).
- `>=` e `<=` têm bug: use `>` e `<`.
- Sem precedência de operadores: tudo é da esquerda para a direita. Use variáveis temporárias.
- Sem leitura de array por índice (`A[i]` não existe): use `charAt`, `split`, `shift`, `push`, `join`.
- Funções exigem pelo menos 1 parâmetro.
- Atribuir variável a variável exige operação: `B = A + 0`.
- Chamada de função dentro de `BORA CUMPADI` deve ser atribuída a uma variável antes.

## Arquitetura

- **BIRL**: estado, regras, validação, IA (minimax, BFS, filtragem de dicionário), cálculos de tempo e combate.
- **Python/GTK4**: janela, cliques/teclas, processo filho do BIRL, protocolo de linhas (`TEXT`/`DATA`/`PROMPT`/`END`). Nenhuma regra de jogo.
- **Bash**: `build` e `run.sh`.
- **JSON**: apenas o save do Tamagotchi, gravado pela interface com timestamp.

## Proporção alvo

Mantenha a maior proporção possível de código em BIRL (atualmente ~71,7% das linhas de código são BIRL).

## CI

Cada PR e push dispara o GitHub Actions que:
1. Compila o BIRL (`build` + `birl main.birl`)
2. Checa sintaxe/estilo do Python (ruff)
3. Roda shellcheck no `run.sh`
4. Roda testes de regressão

A GUI GTK4 e o áudio não rodam no CI (sem display).
