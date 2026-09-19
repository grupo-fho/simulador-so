package so;

import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;

record Configuracao(Path carga, Escalonador.Politica politica, int quantum, int troca,
                    int pagina, int molduras, int falta, int disco, int terminal,
                    long semente, Path saida) {
    static Configuracao ler(String[] argumentos) {
        Map<String, String> opcoes = new LinkedHashMap<>();
        for (int indice = 0; indice < argumentos.length; indice += 2) {
            String chave = argumentos[indice];
            if (!chave.matches("--(carga|politica|quantum|troca|pagina|molduras|falta|disco|terminal|semente|saida)")) {
                throw new IllegalArgumentException("Opção desconhecida: " + chave);
            }
            if (indice + 1 == argumentos.length || opcoes.putIfAbsent(chave, argumentos[indice + 1]) != null) {
                throw new IllegalArgumentException("Opção repetida ou sem valor: " + chave);
            }
        }
        if (!opcoes.containsKey("--carga")) {
            throw new IllegalArgumentException("Informe --carga caminho.txt; consulte --ajuda.");
        }
        Escalonador.Politica politica;
        try {
            politica = Escalonador.Politica.valueOf(opcoes.getOrDefault("--politica", "FCFS"));
        } catch (IllegalArgumentException erro) {
            throw new IllegalArgumentException("Política deve ser FCFS, RR ou PRIORIDADE.");
        }
        long semente;
        try {
            semente = Long.parseLong(opcoes.getOrDefault("--semente", "42"));
        } catch (NumberFormatException erro) {
            throw new IllegalArgumentException("Semente deve ser um inteiro de 64 bits.");
        }
        return new Configuracao(Path.of(opcoes.get("--carga")), politica,
                inteiro(opcoes, "quantum", 3, 1), inteiro(opcoes, "troca", 1, 0),
                inteiro(opcoes, "pagina", 16, 1), inteiro(opcoes, "molduras", 4, 1),
                inteiro(opcoes, "falta", 5, 1), inteiro(opcoes, "disco", 4, 1),
                inteiro(opcoes, "terminal", 2, 1), semente,
                Path.of(opcoes.getOrDefault("--saida", "resultados/execucao")));
    }

    private static int inteiro(Map<String, String> opcoes, String nome, int padrao, int minimo) {
        try {
            int valor = Integer.parseInt(opcoes.getOrDefault("--" + nome, Integer.toString(padrao)));
            if (valor < minimo || valor > 1_000_000) {
                throw new NumberFormatException();
            }
            return valor;
        } catch (NumberFormatException erro) {
            throw new IllegalArgumentException("--" + nome + " deve estar entre " + minimo + " e 1000000.");
        }
    }
}
