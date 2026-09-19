package so;

import java.util.List;

record Instrucao(String operacao, List<String> argumentos, int linha) {
    String argumento(int indice) { return argumentos.get(indice); }
    int numero(int indice) { return Integer.parseInt(argumento(indice)); }
}
