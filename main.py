"""Ponto de entrada: python -B main.py --ajuda."""

import sys

# Evita que a aplicação gere arquivos __pycache__ no computador da apresentação.
sys.dont_write_bytecode = True

from simulador.terminal import main


if __name__ == "__main__":
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    raise SystemExit(main())
