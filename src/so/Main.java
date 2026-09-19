package so;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public final class Main {
    private Main() { }

    public static void main(String[] argumentos) {
        if (argumentos.length == 1 && argumentos[0].equals("--ajuda")) {
            System.out.println("""
                    Simulador de SO — Java 21+
                    java -cp build/classes so.Main --carga cargas/mista.txt [opções]
                    --politica FCFS|RR|PRIORIDADE (FCFS)   --quantum N (3)
                    --troca N (1; aceita zero)            --pagina N (16)
                    --molduras N (4)                     --falta N (5)
                    --disco N (4)                        --terminal N (2)
                    --semente N (42; modelo determinístico, sem sorteios)
                    --saida diretório (resultados/execucao; deve estar vazio)
                    N: inteiro positivo até 1000000, exceto troca e semente.
                    Prioridade não preemptiva: menor número tem maior prioridade.
                    """);
            return;
        }
        try {
            Configuracao configuracao = Configuracao.ler(argumentos);
            Simulador simulador = executar(configuracao);
            System.out.print(simulador.metricas().resumoCsv());
            System.out.println("Resultados: " + configuracao.saida().toAbsolutePath());
        } catch (IllegalArgumentException | IOException erro) {
            System.err.println("Erro: " + erro.getMessage());
            System.exit(2);
        }
    }

    // Fluxo compartilhado pela CLI e pela interface; não encerra a JVM em caso de erro.
    static Simulador executar(Configuracao configuracao) throws IOException {
        List<Processo> processos = Carga.ler(configuracao.carga());
        validarEnderecos(processos, configuracao.pagina());
        Path saida = configuracao.saida();
        if (Files.exists(saida)) {
            if (!Files.isDirectory(saida)) { throw new IllegalArgumentException("Saída não é um diretório: " + saida); }
            try (java.util.stream.Stream<Path> arquivos = Files.list(saida)) {
                if (arquivos.findAny().isPresent()) { throw new IllegalArgumentException("Diretório de saída não está vazio: " + saida); }
            }
        }
        Simulador simulador = new Simulador(configuracao, processos);
        simulador.simular();
        Files.createDirectories(saida);
        Metricas metricas = simulador.metricas();
        Files.write(saida.resolve("eventos.log"), simulador.registro(), StandardCharsets.UTF_8);
        Files.writeString(saida.resolve("resumo.csv"), metricas.resumoCsv(), StandardCharsets.UTF_8);
        Files.writeString(saida.resolve("threads.csv"), metricas.threadsCsv(), StandardCharsets.UTF_8);
        Files.writeString(saida.resolve("processos.csv"), metricas.processosCsv(), StandardCharsets.UTF_8);
        return simulador;
    }

    static void validarEnderecos(List<Processo> processos, int tamanhoPagina) {
        for (Processo processo : processos) {
            for (ThreadSimulada thread : processo.threads) {
                for (Instrucao instrucao : thread.instrucoes) {
                    if (instrucao.operacao().equals("MEM") && (long) instrucao.numero(0) >= (long) processo.paginas * tamanhoPagina) {
                        throw new IllegalArgumentException("Linha " + instrucao.linha() + ": endereço fora de " + processo.id);
                    }
                }
            }
        }
    }
}
