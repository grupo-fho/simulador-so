package so;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

// Este objeto é o TCB; pilha e registradores nunca são os da JVM hospedeira.
final class ThreadSimulada {
    final String id;
    final Processo processo;
    final List<Instrucao> instrucoes = new ArrayList<>();
    final Deque<Long> pilha = new ArrayDeque<>();
    final List<String> caixaEntrada = new ArrayList<>();
    private Estado estado = Estado.NOVO;
    int contadorPrograma;
    int restanteSurto;
    long acumulador;
    long entrouPronto;
    long ordemPronto;
    long espera;
    long primeiraCpu = -1;
    long fim = -1;
    long cpu;

    ThreadSimulada(String id, Processo processo) { this.id = id; this.processo = processo; }
    String nome() { return processo.id + "/" + id; }
    Estado estado() { return estado; }

    void mudarEstado(Estado destino, Simulador simulador, String causa) {
        if (causa == null || causa.isBlank() || !estado.permite(destino)) {
            throw new IllegalStateException("Transição inválida de " + nome() + ": " + estado + " -> " + destino);
        }
        if (estado == Estado.PRONTO) { espera += simulador.clock() - entrouPronto; }
        if (destino == Estado.PRONTO) { entrouPronto = simulador.clock(); }
        simulador.log("ESTADO_THREAD", nome(), estado + " -> " + destino + "; causa=" + causa);
        estado = destino;
        if (destino == Estado.FINALIZADO) { fim = simulador.clock(); }
        processo.atualizarEstado(simulador, causa);
    }
}
