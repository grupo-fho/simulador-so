package so;

import java.util.ArrayDeque;
import java.util.Deque;

final class Memoria {
    static final class Pagina {
        boolean presente;
        int moldura = -1;
    }
    private record Residente(Processo processo, int pagina) { }
    private record Falta(ThreadSimulada thread, int pagina, int deslocamento) { }
    private final Simulador simulador;
    private final int tamanhoPagina;
    private final int tempoFalta;
    private final Residente[] molduras;
    private final Deque<Integer> ordemFifo = new ArrayDeque<>();
    private final Deque<Falta> pendentes = new ArrayDeque<>();
    long referencias;
    long faltas;
    long acertos;

    Memoria(Simulador simulador, Configuracao configuracao) {
        this.simulador = simulador;
        tamanhoPagina = configuracao.pagina();
        tempoFalta = configuracao.falta();
        molduras = new Residente[configuracao.molduras()];
    }

    boolean acessar(ThreadSimulada thread, int endereco) {
        int pagina = endereco / tamanhoPagina;
        int deslocamento = endereco % tamanhoPagina;
        if (endereco < 0 || pagina >= thread.processo.paginas) {
            throw new IllegalArgumentException("Endereço lógico fora do processo: " + endereco);
        }
        referencias++;
        Pagina entrada = thread.processo.tabelaPaginas.computeIfAbsent(pagina, chave -> new Pagina());
        if (entrada.presente) {
            acertos++;
            traduzir(thread, pagina, deslocamento, entrada.moldura, "ACERTO_MEMORIA");
            return true;
        }
        faltas++;
        simulador.log("FALTA_PAGINA", thread.nome(), "pagina=" + pagina);
        simulador.bloquear(thread, "falta de página " + pagina);
        pendentes.addLast(new Falta(thread, pagina, deslocamento));
        if (pendentes.size() == 1) { iniciarAtendimento(); }
        return false;
    }

    private void iniciarAtendimento() {
        Falta falta = pendentes.peekFirst();
        simulador.log("INICIO_PAGINACAO", falta.thread().nome(), "pagina=" + falta.pagina());
        simulador.agendar(simulador.clock() + tempoFalta, 0, this::concluirAtendimento);
    }

    private void concluirAtendimento() {
        Falta falta = pendentes.removeFirst();
        Processo processo = falta.thread().processo;
        Pagina entrada = processo.tabelaPaginas.get(falta.pagina());
        // Outra thread pode ter solicitado a mesma página enquanto ela não estava presente.
        if (!entrada.presente) {
            int moldura = escolherMoldura();
            Residente vitima = molduras[moldura];
            if (vitima != null) {
                Pagina removida = vitima.processo().tabelaPaginas.get(vitima.pagina());
                removida.presente = false;
                removida.moldura = -1;
                simulador.log("SUBSTITUICAO_FIFO", vitima.processo().id,
                        "pagina=" + vitima.pagina() + "; moldura=" + moldura);
            }
            molduras[moldura] = new Residente(processo, falta.pagina());
            entrada.presente = true;
            entrada.moldura = moldura;
            ordemFifo.addLast(moldura);
            simulador.log("CARREGAMENTO_PAGINA", processo.id, "pagina=" + falta.pagina() + "; moldura=" + moldura);
        }
        traduzir(falta.thread(), falta.pagina(), falta.deslocamento(), entrada.moldura, "TRADUCAO_APOS_FALTA");
        processo.salvarContexto(falta.thread());
        simulador.log("INTERRUPCAO_PAGINA", falta.thread().nome(), "Referência concluída pelo paginador.");
        simulador.tornarPronta(falta.thread(), "página disponível");
        if (!pendentes.isEmpty()) { iniciarAtendimento(); }
    }

    private int escolherMoldura() {
        for (int indice = 0; indice < molduras.length; indice++) {
            if (molduras[indice] == null) { return indice; }
        }
        return ordemFifo.removeFirst();
    }

    private void traduzir(ThreadSimulada thread, int pagina, int deslocamento, int moldura, String evento) {
        long fisico = (long) moldura * tamanhoPagina + deslocamento;
        thread.acumulador = fisico;
        simulador.log(evento, thread.nome(), "pagina=" + pagina + "; deslocamento=" + deslocamento + "; fisico=" + fisico);
    }

    void liberar(Processo processo) {
        for (int indice = 0; indice < molduras.length; indice++) {
            if (molduras[indice] != null && molduras[indice].processo() == processo) {
                molduras[indice] = null;
                ordemFifo.remove(Integer.valueOf(indice));
            }
        }
        processo.tabelaPaginas.clear();
        simulador.log("LIBERACAO_MEMORIA", processo.id, "Espaço de endereçamento liberado.");
    }
}
