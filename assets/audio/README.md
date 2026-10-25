# Áudio do BIRL Arcade

Coloque aqui os arquivos de áudio (.ogg ou .wav) fornecidos por você.

## Arquivos esperados (conforme manifest.txt)

| ID | Arquivo | Usado em |
|---|---|---|
| hora_do_show | hora_do_show.ogg | Início do jogo/batalha, habilidade "HORA DO SHOW" |
| birl | birl.ogg | Golpe forte ("BIRL!") e crítico |
| ajuda_o_maluco | ajuda_o_maluco.ogg | Cura "AJUDA O MALUCO TA DOENTE" |
| acerto | acerto.ogg | Jogador ou inimigo acerta um ataque |
| erro | erro.ogg | Jogador ou inimigo erra um ataque |
| vitoria | vitoria.ogg | Vitória na dungeon |
| derrota | derrota.ogg | Derrota na dungeon |

## Direitos autorais

Não gere, não baixe e não copie áudio de vozes de pessoas reais nem cortes de terceiros. Os arquivos são fornecidos por você.

Se preferir não publicar os áudios, esta pasta fica no .gitignore e o jogo funciona silenciosamente sem eles.

## Controles

- Tecla `M`: mutar/desmutar todos os sons
- Volume ajustável na GUI (via manifest/arquivo)

## Reprodução

O jogo usa `paplay` (PulseAudio) ou `aplay` (ALSA) via subprocess para tocar os sons em segundo plano, sem travar o jogo.

Dependências de apt (Pop!_OS 24.04):
```bash
sudo apt install -y pulseaudio-utils alsa-utils
```
(paplay vem com pulseaudio-utils; aplay vem com alsa-utils)
