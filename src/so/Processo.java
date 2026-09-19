package so;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

// Este objeto é o PCB. Campos mutáveis são internos ao pacote do simulador.
final class Processo {
    final String id;
    final long chegada;
    final int prioridade;
    final int paginas;
    final List<ThreadSimulada> threads = new ArrayList<>();
    final Map<Integer, Memoria.Pagina> tabelaPaginas = new LinkedHashMap<>();
    final Map<Integer, Integer> arquivosAbertos = new LinkedHashMap<>();
    private Estado estado = Estado.NOVO;
    int proximoDescritor = 3;
    int operacoesPendentes;
    long fim = -1;
    int contadorPrograma;
    long registradorAcumulador;
    String ultimaThread = "-";

    Processo(String id, long chegada, int prioridade, int paginas) {
        this.id = id;
        this.chegada = chegada;
        this.prioridade = prioridade;
        this.paginas = paginas;
    }

    Estado estado() { return estado; }

    void atualizarEstado(Simulador simulador, String causa) {
        boolean executando = false;
        boolean pronto = false;
        boolean todasFinalizadas = true;
        for (ThreadSimulada thread : threads) {
            executando |= thread.estado() == Estado.EXECUTANDO;
            pronto |= thread.estado() == Estado.PRONTO;
            todasFinalizadas &= thread.estado() == Estado.FINALIZADO;
        }
        Estado destino;
        if (todasFinalizadas && operacoesPendentes == 0) { destino = Estado.FINALIZADO; }
        else if (executando) { destino = Estado.EXECUTANDO; }
        else if (pronto) { destino = Estado.PRONTO; }
        else { destino = Estado.BLOQUEADO; }
        if (estado != destino) {
            simulador.log("ESTADO_PROCESSO", id, estado + " -> " + destino + "; causa=" + causa);
            estado = destino;
            if (destino == Estado.FINALIZADO) {
                fim = simulador.clock();
                simulador.liberarRecursos(this);
            }
        }
    }

    void salvarContexto(ThreadSimulada thread) {
        contadorPrograma = thread.contadorPrograma;
        registradorAcumulador = thread.acumulador;
        ultimaThread = thread.id;
    }
}
