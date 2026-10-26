#!/usr/bin/env bash
# Testes de regressao do BIRL Arcade.
# Joga cada jogo de verdade (mesmo protocolo da interface grafica) e confere as regras.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d node_modules ]; then
  echo "==> Instalando dependencias (npm install)..."
  npm install --no-audit --no-fund
fi

echo "==> Compilando BIRL (build)..."
./build

echo "==> Conferindo que o main.birl transpila e inicia..."
# stdin vazio: o jogo imprime o menu e termina em "END EOF" em vez de esperar o teclado.
SAIDA_INICIAL=$(BIRL_MODE=gui BIRL_GAME=velha timeout 30 node node_modules/birl-js/index.js main.birl < /dev/null 2>&1 || true)
case "$SAIDA_INICIAL" in
  *"END EOF"*) ;;
  *) echo "FALHA: main.birl nao iniciou direito:"; echo "$SAIDA_INICIAL" | head -20; exit 1 ;;
esac
echo "OK: main.birl transpila e inicia."

echo "==> Conferindo a sintaxe do Python da interface..."
python3 -m py_compile gui/*.py tools/*.py
echo "OK: Python compila."

echo "==> Rodando os testes dos jogos..."
timeout 900 python3 -m unittest discover -s tests -v
