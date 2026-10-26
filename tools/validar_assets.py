#!/usr/bin/env python3
"""Confere quais retratos (PNG) e audios (OGG/WAV) ja existem em assets/.

Uso: python3 tools/validar_assets.py
Nada disso e obrigatorio: o jogo funciona sem os arquivos (mostra uma letra no lugar do
retrato e fica em silencio no lugar do som).
"""
import struct
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RETRATOS = RAIZ / "assets" / "portraits"
AUDIO = RAIZ / "assets" / "audio"
TAMANHO_PADRAO = (96, 96)

PERSONAGENS = {
    "bambam": "personagem jogavel",
    "toguro": "personagem jogavel",
    "felipe": "personagem jogavel",
    "frango_mutante": "inimigo (fase 1)",
    "personal_chato": "inimigo (fase 2)",
    "dono_academia": "chefe (fase 3)",
}


def tamanho_png(caminho: Path):
    with caminho.open("rb") as arq:
        cab = arq.read(24)
    if cab[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", cab[16:24])


def main() -> int:
    problemas = 0
    print(f"== Retratos (PNG {TAMANHO_PADRAO[0]}x{TAMANHO_PADRAO[1]}) em assets/portraits/ ==")
    for nome, papel in PERSONAGENS.items():
        caminho = RETRATOS / f"{nome}.png"
        if not caminho.exists():
            print(f"  FALTA   {nome}.png  ({papel})")
            continue
        tam = tamanho_png(caminho)
        if tam is None:
            print(f"  ERRO    {nome}.png nao e um PNG valido")
            problemas += 1
        elif tam != TAMANHO_PADRAO:
            print(f"  AVISO   {nome}.png tem {tam[0]}x{tam[1]} (padrao {TAMANHO_PADRAO[0]}x{TAMANHO_PADRAO[1]})")
        else:
            print(f"  ok      {nome}.png")
    extras = sorted(p.stem for p in RETRATOS.glob("*.png") if p.stem not in PERSONAGENS)
    for nome in extras:
        print(f"  EXTRA   {nome}.png (id desconhecido; so e usado se o BIRL pedir esse id)")

    print("== Audios em assets/audio/ (ids do manifest.txt) ==")
    manifesto = AUDIO / "manifest.txt"
    if manifesto.exists():
        for linha in manifesto.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            ident, _, arquivo = linha.partition("=")
            existe = (AUDIO / arquivo).exists()
            print(f"  {'ok     ' if existe else 'FALTA  '} {ident} -> {arquivo}")
    else:
        print("  manifest.txt nao encontrado")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
