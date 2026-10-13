#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
if ! command -v java >/dev/null 2>&1; then
    echo 'Erro: Java nao encontrado. Instale um JDK 21 ou superior e adicione sua pasta bin ao PATH.' >&2
    exit 1
fi

# Consulta o compilador pelo mesmo executavel usado na compilacao.
versao=$(java -m jdk.compiler/com.sun.tools.javac.Main --version 2>&1) || {
    echo 'Erro: e necessario um JDK 21 ou superior com o modulo jdk.compiler. Ajuste JAVA_HOME e PATH; um JRE nao e suficiente.' >&2
    exit 1
}
versao_principal=$(printf '%s\n' "$versao" | sed -n 's/^javac \([0-9][0-9]*\)\([. +\-].*\)\{0,1\}$/\1/p')
if [ -z "$versao_principal" ] || [ "$versao_principal" -lt 21 ]; then
    echo 'Erro: e necessario um JDK 21 ou superior. Confira java -version e ajuste JAVA_HOME e PATH para o JDK desejado.' >&2
    exit 1
fi

mkdir -p build/classes build/test
java -m jdk.compiler/com.sun.tools.javac.Main --release 21 -encoding UTF-8 -Xlint:all -d build/classes src/so/*.java
java -m jdk.compiler/com.sun.tools.javac.Main --release 21 -encoding UTF-8 -Xlint:all -cp build/classes -d build/test test/so/*.java
