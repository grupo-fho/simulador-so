#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
sh scripts/compilar.sh
java -cp build/classes:build/test so.Testes
java -Djava.awt.headless=true -cp build/classes:build/test so.TestesInterface

java -cp build/classes:build/test so.TestesDoom
