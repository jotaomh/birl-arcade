#!/usr/bin/env bash
# Testes de regressão do BIRL Arcade.
# Compila o BIRL, verifica a transpilação e roda cada jogo no terminal
# com entradas fixas, comparando a saída esperada (presença de linhas-chave).
set -euo pipefail
cd "$(dirname "$0")"

ERROS=0

echo "==> Compilando BIRL (build)..."
./build

echo "==> Verificando transpilação do main.birl..."
if ! npx birl main.birl >/dev/null 2>&1; then
  echo "FALHA: main.birl não transpila."
  ERROS=$((ERROS + 1))
else
  echo "OK: main.birl transpila."
fi

# Função auxiliar: roda o BIRL com entradas e verifica se contém uma string.
# $entradas deve ser uma string com cada entrada em uma linha separada por nova linha.
verificar_saida() {
  local jogo="$1"
  local entradas="$2"
  local esperado="$3"
  local saida
  saida=$(printf '%s\n' "$entradas" | timeout 20 node node_modules/birl-js/index.js main.birl 2>&1 || true)
  if echo "$saida" | grep -qF "$esperado"; then
    echo "OK: $jogo -> contém '$esperado'"
  else
    echo "FALHA: $jogo -> NÃO contém '$esperado'"
    echo "--- saída ---"
    echo "$saida" | head -30
    echo "-------------"
    ERROS=$((ERROS + 1))
  fi
}

# Definir entradas como variáveis para evitar problemas com $'...' e aspas
entradas_velha=$'1\n4\n0'
entradas_forca=$'2\nSUPINO\n\n'
entradas_academia=$'3\n1\n5\n0'
entradas_tamagotchi=$'4\n0'
entradas_dungeon=$'5\n1'
entradas_le_linha=$'2\nABACATE\n\n\n\n0\n'
entradas_forca_freq=$'2\nSUPINO\n\n\n\n\n\n0\n'
entradas_forca_errada=$'2\nSUPINO\nA\n\n\n\n0\n'

echo "==> Teste: Jogo da Velha..."
verificar_saida "velha" "$entradas_velha" "JOGO DA VELHA"

echo "==> Teste: Forca..."
verificar_saida "forca" "$entradas_forca" "FORCA"

echo "==> Teste: Academia..."
verificar_saida "academia" "$entradas_academia" "SIMULADOR DE ACADEMIA"

echo "==> Teste: Tamagotchi..."
verificar_saida "tamagotchi" "$entradas_tamagotchi" "TAMAGOTCHI DO MONSTRO"

echo "==> Teste: Dungeon RPG..."
verificar_saida "dungeon" "$entradas_dungeon" "DUNGEON DA ACADEMIA RPG"

echo "==> Teste: LE_LINHA com acentos..."
verificar_saida "le_linha" "$entradas_le_linha" "_______"

echo "==> Teste: Forca chuta por frequencia (não ordem alfabética)..."
verificar_saida "forca_freq" "$entradas_forca_freq" "CHUTA O"

echo "==> Teste: Forca elimina palavras com letra errada..."
verificar_saida "forca_errada" "$entradas_forca_errada" "CHUTA O"

echo ""
if [ "$ERROS" -eq 0 ]; then
  echo "Todos os testes de regressão passaram."
  exit 0
else
  echo "$ERROS teste(s) falharam."
  exit 1
fi
