#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
sh scripts/compilar.sh
java -cp build/classes so.InterfaceGrafica
