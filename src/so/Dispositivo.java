package so;

import java.util.ArrayDeque;
import java.util.Deque;

final class Dispositivo {
    private record Requisicao(long id, ThreadSimulada thread, boolean bloqueante) { }
    private final Simulador simulador;
    final String nome;
    private final String tipo;
    private final int tempoServico;
    private final Deque<Requisicao> fila = new ArrayDeque<>();
    private long proximoId;
    long ocupado;

    Dispositivo(Simulador simulador, String nome, String tipo, int tempoServico) {
        this.simulador = simulador;
        this.nome = nome;
        this.tipo = tipo;
        this.tempoServico = tempoServico;
    }

    void solicitar(ThreadSimulada thread, boolean bloqueante) {
        Requisicao requisicao = new Requisicao(++proximoId, thread, bloqueante);
        thread.processo.operacoesPendentes++;
        simulador.log("SOLICITACAO_IO", thread.nome(), nome + " requisicao=" + requisicao.id() + "; bloqueante=" + bloqueante);
        if (bloqueante) { simulador.bloquear(thread, "E/S " + nome); }
        fila.addLast(requisicao);
        if (fila.size() == 1) { iniciarServico(); }
    }

    private void iniciarServico() {
        Requisicao requisicao = fila.peekFirst();
        simulador.log("INICIO_IO", requisicao.thread().nome(), nome + "; tipo=" + tipo + "; estado=OCUPADO; requisicao=" + requisicao.id());
        simulador.agendar(simulador.clock() + tempoServico, 0, this::concluirServico);
    }

    private void concluirServico() {
        Requisicao requisicao = fila.removeFirst();
        ThreadSimulada thread = requisicao.thread();
        ocupado += tempoServico;
        thread.processo.operacoesPendentes--;
        String resultado = nome + ":" + requisicao.id() + ":OK";
        thread.caixaEntrada.add(resultado);
        simulador.log("INTERRUPCAO_IO", thread.nome(), "resultado=" + resultado + "; entrega=caixaEntrada; pendentes=" + fila.size());
        if (requisicao.bloqueante()) { simulador.tornarPronta(thread, "interrupção " + nome); }
        else { thread.processo.atualizarEstado(simulador, "conclusão assíncrona " + nome); }
        if (!fila.isEmpty()) { iniciarServico(); }
        else { simulador.log("DISPOSITIVO_LIVRE", nome, "estado=LIVRE"); }
    }
}
