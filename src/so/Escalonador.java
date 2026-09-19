package so;

import java.util.Comparator;
import java.util.PriorityQueue;

final class Escalonador {
    enum Politica { FCFS, RR, PRIORIDADE }
    private final PriorityQueue<ThreadSimulada> prontos;
    private long sequencia;

    Escalonador(Politica politica) {
        Comparator<ThreadSimulada> ordem = Comparator.comparingLong(thread -> thread.ordemPronto);
        if (politica == Politica.PRIORIDADE) {
            ordem = Comparator.comparingInt((ThreadSimulada thread) -> thread.processo.prioridade).thenComparing(ordem);
        }
        prontos = new PriorityQueue<>(ordem.thenComparing(ThreadSimulada::nome));
    }

    void adicionar(ThreadSimulada thread) {
        if (thread.estado() != Estado.PRONTO || prontos.contains(thread)) {
            throw new IllegalStateException("Inserção inválida na fila: " + thread.nome());
        }
        thread.ordemPronto = sequencia++;
        prontos.add(thread);
    }
    ThreadSimulada retirar() { return prontos.remove(); }
    boolean temProntos() { return !prontos.isEmpty(); }
}
