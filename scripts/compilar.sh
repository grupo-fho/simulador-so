#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p build/classes build/test
java -m jdk.compiler/com.sun.tools.javac.Main --release 21 -encoding UTF-8 -Xlint:all -d build/classes src/so/*.java
java -m jdk.compiler/com.sun.tools.javac.Main --release 21 -encoding UTF-8 -Xlint:all -cp build/classes -d build/test test/so/*.java
