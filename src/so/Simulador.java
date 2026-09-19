package so;

import java.util.ArrayList;
import java.util.List;
import java.util.PriorityQueue;

final class Simulador {
    private final Configuracao configuracao;
    private final List<Processo> processos;
    private final PriorityQueue<Evento> eventos = new PriorityQueue<>();
    private final List<String> registro = new ArrayList<>();
    private final Escalonador escalonador;
    final Memoria memoria;
    private final Arquivos arquivos = new Arquivos();
    private final Dispositivo disco;
    private final Dispositivo terminal;
    private long clock;
    private long sequenciaEvento;
    private ThreadSimulada executando;
    private boolean trocandoContexto;
    private int consumoQuantum;
    private long cpuUtil;
    private long trocas;
    private long sobrecarga;
    private long errosOperacao;
    private boolean iniciada;

    Simulador(Configuracao configuracao, List<Processo> processos) {
        this.configuracao = configuracao;
        this.processos = List.copyOf(processos);
        escalonador = new Escalonador(configuracao.politica());
        memoria = new Memoria(this, configuracao);
        disco = new Dispositivo(this, "disco", "bloco", configuracao.disco());
        terminal = new Dispositivo(this, "terminal", "caractere", configuracao.terminal());
    }

    long clock() { return clock; }
    List<String> registro() { return List.copyOf(registro); }

    void log(String tipo, String objeto, String descricao) {
        registro.add(clock + " | " + tipo + " | " + objeto + " | " + descricao);
    }

    void agendar(long instante, int ordemTipo, Runnable acao) {
        if (instante < clock) { throw new IllegalArgumentException("Evento no passado."); }
        eventos.add(new Evento(instante, ordemTipo, sequenciaEvento++, acao));
    }

    void simular() {
        if (iniciada) { throw new IllegalStateException("Crie outro simulador para repetir a execução."); }
        iniciada = true;
        log("CONFIGURACAO", "sistema", configuracao.toString());
        log("MODELO", "sistema", "Prioridade não preemptiva; menor valor vence; semente registrada, sem aleatoriedade.");
        for (Processo processo : processos) {
            agendar(processo.chegada, 1, () -> admitir(processo));
        }
        while (!eventos.isEmpty()) {
            clock = eventos.peek().instante();
            // Conclusões externas (0), chegadas (1), CPU (2), fim de troca (3).
            while (!eventos.isEmpty() && eventos.peek().instante() == clock) {
                eventos.remove().acao().run();
            }
            if (executando == null && !trocandoContexto && escalonador.temProntos()) {
                iniciarTroca();
            }
        }
        for (Processo processo : processos) {
            if (processo.estado() != Estado.FINALIZADO) {
                throw new IllegalStateException("Simulação terminou com processo pendente: " + processo.id);
            }
        }
        log("FIM_SIMULACAO", "sistema", "Todos os processos e requisições concluídos.");
    }

    private void admitir(Processo processo) {
        log("CHEGADA", processo.id, "prioridade=" + processo.prioridade + "; paginas=" + processo.paginas);
        for (ThreadSimulada thread : processo.threads) { tornarPronta(thread, "admissão"); }
        log("ADMISSAO", processo.id, "threads=" + processo.threads.size());
    }

    void tornarPronta(ThreadSimulada thread, String causa) {
        thread.mudarEstado(Estado.PRONTO, this, causa);
        escalonador.adicionar(thread);
        log("FILA_PRONTOS", thread.nome(), "causa=" + causa);
    }

    private void iniciarTroca() {
        trocandoContexto = true;
        trocas++;
        log("INICIO_TROCA", "CPU", "custo=" + configuracao.troca());
        agendar(clock + configuracao.troca(), 3, this::despachar);
    }

    private void despachar() {
        trocandoContexto = false;
        sobrecarga += configuracao.troca();
        log("FIM_TROCA", "CPU", "Seleção entre as threads prontas neste instante.");
        executando = escalonador.retirar();
        consumoQuantum = 0;
        executando.mudarEstado(Estado.EXECUTANDO, this, "despacho");
        log("DESPACHO", executando.nome(), "pc=" + executando.contadorPrograma + "; acumulador=" + executando.acumulador);
        if (executando.contadorPrograma == executando.instrucoes.size()) { finalizarThread(); }
        else { iniciarInstrucao(); }
    }

    private void iniciarInstrucao() {
        if (executando.primeiraCpu < 0) { executando.primeiraCpu = clock; }
        agendar(clock + 1, 2, this::concluirInstrucao);
    }

    private void concluirInstrucao() {
        ThreadSimulada thread = executando;
        Instrucao instrucao = thread.instrucoes.get(thread.contadorPrograma);
        cpuUtil++;
        thread.cpu++;
        consumoQuantum++;
        log("INSTRUCAO", thread.nome(), "pc=" + thread.contadorPrograma + "; " + instrucao.operacao() + " " + instrucao.argumentos());
        if (instrucao.operacao().equals("CPU")) {
            if (thread.restanteSurto == 0) { thread.restanteSurto = instrucao.numero(0); }
            thread.restanteSurto--;
            thread.acumulador++;
            if (thread.restanteSurto == 0) { thread.contadorPrograma++; }
        } else {
            // MEM é concluída pelo paginador em caso de falta, sem repetir a referência.
            thread.contadorPrograma++;
            try { executarOperacao(thread, instrucao); }
            catch (IllegalArgumentException erro) {
                errosOperacao++;
                log("ERRO_OPERACAO", thread.nome(), "linha=" + instrucao.linha() + "; " + erro.getMessage());
            }
        }
        thread.processo.salvarContexto(thread);
        if (executando == null) { return; }
        if (thread.contadorPrograma == thread.instrucoes.size()) { finalizarThread(); }
        else if (configuracao.politica() == Escalonador.Politica.RR && consumoQuantum == configuracao.quantum()) {
            log("PREEMPCAO", thread.nome(), "Quantum esgotado.");
            executando = null;
            tornarPronta(thread, "fim de quantum");
        } else { iniciarInstrucao(); }
    }

    private void executarOperacao(ThreadSimulada thread, Instrucao instrucao) {
        Processo processo = thread.processo;
        switch (instrucao.operacao()) {
            case "MEM" -> memoria.acessar(thread, instrucao.numero(0));
            case "IO" -> {
                Dispositivo dispositivo = instrucao.argumento(0).equals("disco") ? disco : terminal;
                dispositivo.solicitar(thread, instrucao.argumento(1).equals("B"));
            }
            case "EMPILHAR" -> thread.pilha.push((long) instrucao.numero(0));
            case "DESEMPILHAR" -> {
                if (thread.pilha.isEmpty()) { throw new IllegalArgumentException("Pilha lógica vazia."); }
                thread.acumulador = thread.pilha.pop();
            }
            case "CRIAR", "MKDIR" -> {
                arquivos.criar(instrucao.argumento(0), instrucao.operacao().equals("MKDIR"), instrucao.argumento(1), clock);
                log("CRIACAO_ARQUIVO", thread.nome(), instrucao.argumento(0));
            }
            case "ABRIR" -> {
                int descritor = arquivos.abrir(processo, instrucao.argumento(0), instrucao.argumento(1));
                thread.acumulador = descritor;
                log("ABERTURA_ARQUIVO", thread.nome(), instrucao.argumento(0) + "; descritor=" + descritor);
            }
            case "LER" -> {
                String texto = arquivos.ler(processo, instrucao.numero(0), instrucao.numero(1));
                thread.acumulador = texto.length();
                log("LEITURA_ARQUIVO", thread.nome(), "descritor=" + instrucao.numero(0) + "; texto=" + texto);
            }
            case "ESCREVER" -> {
                arquivos.escrever(processo, instrucao.numero(0), instrucao.argumento(1), clock);
                log("ESCRITA_ARQUIVO", thread.nome(), "descritor=" + instrucao.numero(0) + "; unidades=" + instrucao.argumento(1).length());
            }
            case "FECHAR" -> {
                arquivos.fechar(processo, instrucao.numero(0));
                log("FECHAMENTO_ARQUIVO", thread.nome(), "descritor=" + instrucao.numero(0));
            }
            case "REMOVER" -> { arquivos.remover(instrucao.argumento(0), clock); log("REMOCAO_ARQUIVO", thread.nome(), instrucao.argumento(0)); }
            case "LISTAR" -> log("LISTAGEM", thread.nome(), arquivos.listar(instrucao.argumento(0)));
            default -> throw new IllegalStateException("Instrução não implementada: " + instrucao.operacao());
        }
    }

    void bloquear(ThreadSimulada thread, String causa) {
        if (executando != thread) { throw new IllegalStateException("Somente a thread na CPU pode bloquear."); }
        log("BLOQUEIO", thread.nome(), causa);
        executando = null;
        thread.mudarEstado(Estado.BLOQUEADO, this, causa);
    }

    private void finalizarThread() {
        ThreadSimulada thread = executando;
        executando = null;
        log("FINALIZACAO_THREAD", thread.nome(), "pc=" + thread.contadorPrograma + "; acumulador=" + thread.acumulador);
        thread.mudarEstado(Estado.FINALIZADO, this, "fim do programa");
    }

    void liberarRecursos(Processo processo) {
        for (int descritor : new ArrayList<>(processo.arquivosAbertos.keySet())) {
            arquivos.fechar(processo, descritor);
            log("FECHAMENTO_ARQUIVO", processo.id, "descritor=" + descritor + "; causa=fim do processo");
        }
        memoria.liberar(processo);
        log("FINALIZACAO_PROCESSO", processo.id, "retorno=" + (clock - processo.chegada));
    }

    Metricas metricas() {
        return new Metricas(clock, cpuUtil, sobrecarga, trocas, memoria.referencias, memoria.faltas,
                memoria.acertos, disco.ocupado, terminal.ocupado, errosOperacao, processos);
    }
}
