#!/usr/bin/env bash
# Cria as labels do BIRL Arcade no repositório.
# Uso: ./create-labels.sh
set -euo pipefail

REPO="${1:-jotaomh/birl-arcade}"

echo "Criando labels no $REPO..."

gh label create --repo "$REPO" --file .github/labels.yml 2>/dev/null || {
  echo "Algumas labels já existem ou houve erro. Tentando criar uma a uma..."
  while IFS= read -r line; do
    nome=$(echo "$line" | grep -o '"name": "[^"]*"' | cut -d'"' -f4)
    cor=$(echo "$line" | grep -o '"color": "[^"]*"' | cut -d'"' -f4)
    [ -z "$nome" ] && continue
    gh label create --repo "$REPO" "$nome" --color "$cor" --force 2>/dev/null || true
  done < .github/labels.yml
}

echo "Labels criadas/atualizadas com sucesso."
