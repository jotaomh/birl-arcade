# Correções desta rodada

## O que estava quebrado e foi consertado

**Dungeon**
- Na interface gráfica o jogo **travava**: a escolha de personagem e o movimento liam o teclado direto, sem avisar a janela (`PROMPT`). Agora usam o protocolo.
- O mapa da **fase 2 tinha 99 caracteres** (linhas desalinhadas, saída inalcançável). Redesenhado e validado: as 3 fases têm 100 caracteres, borda fechada e tudo alcançável.
- Combate reescrito: antes os dois lados acertavam sempre, o crítico não dobrava o dano, a falha crítica nunca aparecia, habilidades gastavam Pump negativo e não dependiam do personagem, e a porcentagem do Toguro não existia. Agora: d20 + ataque contra defesa (10 + DEF), crítico no 20 (dano dobrado), falha no 1, habilidades por personagem com custo de Pump, **Toguro escolhe 20/50/80/100%**, whey limitado (3), fuga por d20, XP e nível.
- O gerador de dados estava quebrado (sem precedência de operadores) e a semente era sempre a mesma. Trocado por MINSTD exato; `BIRL_SEED` repete a partida.
- `SOM` e `DIALOGO` apareciam como texto cru no modo terminal. Agora o terminal desenha a caixa de diálogo em ASCII e não imprime nada do protocolo.
- Vida passava do máximo (ex.: 52/40) e o resultado da fase final dizia "derrota" ao sair com `Q`.
- **WASD sem Enter no terminal** (modo teclado direto, restaura o terminal ao sair; `Ctrl+C` tratado).

**Forca**
- O resultado estava **invertido**: o Bambam acertava tudo e aparecia "não adivinhou".
- Dicionário cheio de palavras que não existem (AGUJA, UCIGA...). Trocado por 255 palavras reais (academia + dia a dia).
- Sem dicionário, chutava em ordem alfabética; agora segue a frequência do português. Conta palavras (não letras repetidas).
- O estado final (padrão e erros) não era reenviado à interface.

**Tamagotchi**
- Depois de 24 ações o "dia" nunca recomeçava (1 ação por sessão para sempre). Agora amanhece.
- Terminal salvava o horário em milissegundos e a interface em segundos (alternar entre os dois matava o bichinho). Unificado em segundos.
- Save corrompido derrubava o jogo; `BIRL_TEMPO` inválido virava `NaN`.

**Academia**: números quebrados (16.666...), calorias/proteína só cresciam (agora gastam por dia, com fome e pouca proteína), typo "COMa".

**Núcleo**: Enter em CRLF gerava uma linha vazia extra; linha maior que 256 bytes estourava o buffer.

**Interface gráfica**: o retrato PNG **nunca aparecia** (escondia a letra e não mostrava a imagem); caixa de diálogo agora fica embaixo da tela; painel da Dungeon com personagem, nível, Pump, whey, barra do inimigo e mapa; setas e teclas `1`-`5` nas escolhas; o diálogo não bloqueia mais as outras teclas.

**Testes**: o `run-tests.sh` antigo travava (rodava o jogo esperando teclado) e só conferia títulos. Agora são 25 testes que jogam de verdade pelo protocolo; rodam com `./run-tests.sh` em ~35 s. Eu conferi que eles **falham no código antigo**.

## Como rodar
```bash
npm install            # primeira vez
./run.sh               # terminal
./run.sh --gui         # janela GTK4
./run-tests.sh         # testes
python3 tools/validar_assets.py   # quais retratos/áudios faltam
```

## Ainda é com você
- Retratos em `assets/portraits/<id>.png` (96x96) e áudios em `assets/audio/` (veja os READMEs). Sem eles o jogo funciona (inicial no lugar do retrato, silêncio).
- O som só toca no modo gráfico.
- A pasta `.github/` (templates, CI, labels) não estava neste zip, então não mexi nela.
- Balanceamento: com um bot jogando bem, Bambam e Felipe vencem sempre e o Toguro cerca de 75%. Ajuste os números em `D_PERSONAGEM_INIT` e `D_INIM_CADASTRAR`.
