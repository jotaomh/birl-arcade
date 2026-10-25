## Descrição

Descrição sumária das implementações feitas por este PR.

## Tipo de mudança

Marque as opções que se aplicam:

- [ ] Feature (nova funcionalidade)
- [ ] Fix (correção de bug)
- [ ] Hotfix (correção urgente em produção)
- [ ] Audit (auditoria/revisão de segurança ou integridade)
- [ ] Release (corte de release / tag)
- [ ] Chore (tarefa de manutenção, build, CI, docs)

## Jogos afetados

Marque o(s) jogo(s) impactado(s) por esta mudança:

- [ ] jogo:velha
- [ ] jogo:forca
- [ ] jogo:academia
- [ ] jogo:tamagotchi
- [ ] jogo:dungeon
- [ ] nenhum (apenas infraestrutura: build, CI, docs, etc.)

## Como testar no Pop!_OS

Descreva os passos para reproduzir e verificar a mudança localmente:

```bash
# 1. Baixe as dependências
sudo apt update
sudo apt install -y nodejs npm python3-gi python3-gi-cairo gir1.2-gtk-4.0
npm install

# 2. Rode o build e o modo terminal
./build
./run.sh --terminal

# 3. Rode o modo gráfico (GTK4)
./run.sh --gui

# 4. Rode os testes de regressão (quando houver)
npm test
```

Se a mudança afeta um jogo específico, informe qual opção escolher no menu e qual comportamento esperado.

## Mudança visual (prints / GIF)

Se houver alteração na interface gráfica, anexe print ou GIF antes/depois.

- Antes:
- Depois:

## Checklist

- [ ] O BIRL compila (`./build` + `birl main.birl` sem erros)
- [ ] O modo terminal funciona para todos os jogos afetados
- [ ] O modo gráfico (GTK4) abre sem erros para os jogos afetados
- [ ] Testes de regressão passando (`npm test` ou `./run-tests.sh`)
- [ ] Python segue o estilo (ruff/flake8 sem erros novos)
- [ ] `run.sh` passou pelo shellcheck
- [ ] README atualizado, se necessário
- [ ] Nenhuma regra de jogo foi movida do BIRL para o Python (BIRL continua sendo o cérebro)

---

Sai de casa codei pra caralho!™
