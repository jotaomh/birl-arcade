# Retratos (pixel art)

Coloque aqui os PNGs dos personagens e inimigos. Nome do arquivo = id do personagem:

| Arquivo | Quem |
|---|---|
| `bambam.png`, `toguro.png`, `felipe.png` | personagens jogaveis |
| `frango_mutante.png` | inimigo da fase 1 |
| `personal_chato.png` | inimigo da fase 2 |
| `dono_academia.png` | chefe da fase 3 |

- Tamanho recomendado: **96x96** (pixel art, fundo transparente).
- O jogo funciona sem os arquivos: no lugar do retrato aparece a inicial do nome.
- Use apenas arte desenhada por voce ou com licenca livre (CC0/CC-BY, com creditos no README).
  Nada de sprites ripados de jogos/animes nem fotos de pessoas reais.
- Para conferir o que ja existe: `python3 tools/validar_assets.py`.
- Para novos inimigos, o id vem do cadastro em `birl/50_dungeon.birl` (`D_INIM_CADASTRAR`).
