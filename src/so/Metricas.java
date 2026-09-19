package so;

import java.util.List;
import java.util.Locale;

record Metricas(long tempoTotal, long cpuUtil, long sobrecarga, long trocas, long referencias,
                long faltas, long acertos, long discoOcupado, long terminalOcupado,
                long errosOperacao, List<Processo> processos) {
    static String razao(long numerador, long denominador) {
        return String.format(Locale.ROOT, "%.6f", denominador == 0 ? 0.0 : (double) numerador / denominador);
    }

    String resumoCsv() {
        return "tempo_total,cpu_util,sobrecarga,ocioso,utilizacao_cpu,utilizacao_disco,utilizacao_terminal,throughput,trocas,referencias,faltas,taxa_faltas,acertos,erros_operacao\n"
                + tempoTotal + "," + cpuUtil + "," + sobrecarga + "," + (tempoTotal - cpuUtil - sobrecarga) + ","
                + razao(cpuUtil, tempoTotal) + "," + razao(discoOcupado, tempoTotal) + "," + razao(terminalOcupado, tempoTotal) + ","
                + razao(processos.size(), tempoTotal) + "," + trocas + "," + referencias + "," + faltas + ","
                + razao(faltas, referencias) + "," + acertos + "," + errosOperacao + "\n";
    }

    String threadsCsv() {
        StringBuilder texto = new StringBuilder("processo,thread,chegada,fim,retorno,espera,resposta,cpu\n");
        for (Processo processo : processos) {
            for (ThreadSimulada thread : processo.threads) {
                texto.append(processo.id).append(',').append(thread.id).append(',').append(processo.chegada).append(',')
                        .append(thread.fim).append(',').append(thread.fim - processo.chegada).append(',').append(thread.espera)
                        .append(',').append(thread.primeiraCpu - processo.chegada).append(',').append(thread.cpu).append('\n');
            }
        }
        return texto.toString();
    }

    String processosCsv() {
        StringBuilder texto = new StringBuilder("processo,chegada,fim,retorno,espera_soma_threads,resposta\n");
        for (Processo processo : processos) {
            long espera = 0;
            long primeiraCpu = Long.MAX_VALUE;
            for (ThreadSimulada thread : processo.threads) {
                espera += thread.espera;
                primeiraCpu = Math.min(primeiraCpu, thread.primeiraCpu);
            }
            texto.append(processo.id).append(',').append(processo.chegada).append(',').append(processo.fim).append(',')
                    .append(processo.fim - processo.chegada).append(',').append(espera).append(',')
                    .append(primeiraCpu - processo.chegada).append('\n');
        }
        return texto.toString();
    }
}
