#!/usr/bin/env bash
# BIRL Arcade - inicia no terminal (padrao) ou na interface GTK4.
set -euo pipefail
cd "$(dirname "$0")"

./build
mkdir -p saves

MODO="${1:-terminal}"
case "$MODO" in
  --gui|-g|gui)
    if ! python3 -c "import gi; gi.require_version('Gtk','4.0'); from gi.repository import Gtk" 2>/dev/null; then
      echo "GTK4/PyGObject nao encontrado. Instale:" >&2
      echo "  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0" >&2
      exit 1
    fi
    exec python3 gui/app.py "${@:2}"
    ;;
  --terminal|-t|terminal)
    exec ./node_modules/.bin/birl main.birl
    ;;
  *)
    echo "Uso: ./run.sh [--gui|--terminal]" >&2
    exit 2
    ;;
esac
