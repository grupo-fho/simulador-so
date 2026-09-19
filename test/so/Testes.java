package so;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public final class Testes {
    private static int aprovados;
    private Testes() { }

    public static void main(String[] argumentos) throws IOException {
        testarEstados();
        testarFilas();
        testarMetricas();
        testarQuantum();
        testarPrioridades();
        testarTrocaContexto();
        testarMemoria();
        testarIo();
        testarArquivos();
        testarCarga();
        testarIntegracao();
        System.out.println("OK: " + aprovados + " verificações aprovadas.");
    }

    private static Configuracao configuracao(String politica, int quantum, int troca, int molduras) {
        return Configuracao.ler(new String[]{"--carga", "teste.txt", "--politica", politica, "--quantum", "" + quantum,
                "--troca", "" + troca, "--molduras", "" + molduras, "--falta", "2", "--disco", "3", "--terminal", "2"});
    }

    private static Processo processo(String id, int chegada, int prioridade, String... instrucoes) {
        Processo processo = new Processo(id, chegada, prioridade, 8);
        adicionarThread(processo, "T1", instrucoes);
        return processo;
    }

    private static void adicionarThread(Processo processo, String id, String... instrucoes) {
        ThreadSimulada thread = new ThreadSimulada(id, processo);
        for (String texto : instrucoes) {
            List<String> partes = Carga.separar(texto);
            thread.instrucoes.add(new Instrucao(partes.get(0), partes.subList(1, partes.size()), 1));
        }
        processo.threads.add(thread);
    }

    private static Simulador simular(Configuracao configuracao, Processo... processos) {
        Simulador simulador = new Simulador(configuracao, List.of(processos));
        simulador.simular();
        return simulador;
    }

    private static void verificar(boolean condicao, String descricao) {
        if (!condicao) { throw new AssertionError(descricao); }
        aprovados++;
    }

    private static void rejeitar(Runnable operacao, String descricao) {
        try { operacao.run(); }
        catch (IllegalArgumentException | IllegalStateException esperado) { aprovados++; return; }
        throw new AssertionError("Deveria rejeitar: " + descricao);
    }

    private static List<String> objetos(Simulador simulador, String evento) {
        List<String> objetos = new ArrayList<>();
        for (String linha : simulador.registro()) {
            String[] campos = linha.split(" \\| ", 4);
            if (campos[1].equals(evento)) { objetos.add(campos[2]); }
        }
        return objetos;
    }

    private static void testarEstados() {
        verificar(Estado.NOVO.permite(Estado.PRONTO), "Admissão");
        verificar(!Estado.NOVO.permite(Estado.EXECUTANDO), "Novo não pode executar diretamente");
        verificar(!Estado.BLOQUEADO.permite(Estado.EXECUTANDO), "Bloqueado deve voltar à fila");
        verificar(!Estado.FINALIZADO.permite(Estado.PRONTO), "Finalizado é terminal");
        Processo processo = processo("P", 0, 1, "CPU 1");
        Simulador simulador = new Simulador(configuracao("FCFS", 2, 0, 2), List.of(processo));
        rejeitar(() -> processo.threads.get(0).mudarEstado(Estado.PRONTO, simulador, ""), "Causa vazia");
        rejeitar(() -> processo.threads.get(0).mudarEstado(Estado.EXECUTANDO, simulador, "erro"), "Transição ilegal");
    }

    private static void testarFilas() {
        for (String politica : List.of("FCFS", "RR", "PRIORIDADE")) {
            Processo primeiro = processo("A", 0, 5, "CPU 1");
            Processo segundo = processo("B", 0, 1, "CPU 1");
            Simulador simulador = new Simulador(configuracao(politica, 2, 0, 2), List.of(primeiro, segundo));
            Escalonador fila = new Escalonador(Escalonador.Politica.valueOf(politica));
            primeiro.threads.get(0).mudarEstado(Estado.PRONTO, simulador, "teste");
            segundo.threads.get(0).mudarEstado(Estado.PRONTO, simulador, "teste");
            fila.adicionar(primeiro.threads.get(0));
            fila.adicionar(segundo.threads.get(0));
            rejeitar(() -> fila.adicionar(primeiro.threads.get(0)), "Duplicação na fila");
            verificar(fila.retirar().processo.id.equals(politica.equals("PRIORIDADE") ? "B" : "A"), "Ordem " + politica);
        }
    }

    private static void testarMetricas() {
        Processo primeiro = processo("P1", 0, 2, "CPU 3");
        Processo segundo = processo("P2", 1, 1, "CPU 2");
        Simulador simulador = simular(configuracao("FCFS", 2, 0, 2), primeiro, segundo);
        verificar(simulador.clock() == 5 && simulador.metricas().cpuUtil() == 5, "Tempo/CPU FCFS");
        verificar(primeiro.fim == 3 && segundo.fim == 5, "Finalizações FCFS");
        verificar(segundo.threads.get(0).espera == 2 && segundo.threads.get(0).primeiraCpu == 3, "Espera e resposta");
        verificar(simulador.metricas().resumoCsv().contains("1.000000,0.000000,0.000000,0.400000"), "Utilização e throughput");
    }

    private static void testarQuantum() {
        Processo primeiro = processo("P1", 0, 1, "CPU 3");
        Processo segundo = processo("P2", 1, 1, "CPU 2");
        Simulador simulador = simular(configuracao("RR", 2, 0, 2), primeiro, segundo);
        verificar(objetos(simulador, "DESPACHO").equals(List.of("P1/T1", "P2/T1", "P1/T1")), "RR ordem");
        verificar(objetos(simulador, "PREEMPCAO").size() == 1, "Quantum exato");
        verificar(primeiro.fim == 5 && segundo.fim == 4, "RR finalizações");
        verificar(primeiro.threads.get(0).espera == 2 && segundo.threads.get(0).espera == 1, "RR espera");
    }

    private static void testarPrioridades() {
        Simulador simulador = simular(configuracao("PRIORIDADE", 2, 0, 2),
                processo("A", 0, 5, "CPU 4"), processo("B", 1, 0, "CPU 1"), processo("C", 1, 0, "CPU 1"));
        verificar(objetos(simulador, "DESPACHO").equals(List.of("A/T1", "B/T1", "C/T1")), "Prioridade não preemptiva e desempate");
        Simulador duranteTroca = simular(configuracao("PRIORIDADE", 2, 2, 2),
                processo("A", 0, 5, "CPU 1"), processo("B", 1, 0, "CPU 1"));
        verificar(objetos(duranteTroca, "DESPACHO").get(0).equals("B/T1"), "Escolha ao fim da troca");
    }

    private static void testarTrocaContexto() {
        Processo processo = processo("A", 0, 1, "CPU 3");
        Simulador simulador = simular(configuracao("RR", 2, 1, 2), processo);
        verificar(simulador.clock() == 5 && simulador.metricas().sobrecarga() == 2 && simulador.metricas().trocas() == 2, "Custo de redispatch");
        verificar(processo.threads.get(0).espera == 2, "Troca integra espera");
        Simulador ocioso = simular(configuracao("FCFS", 2, 0, 2), processo("A", 5, 1, "CPU 1"));
        verificar(ocioso.clock() == 6 && ocioso.metricas().cpuUtil() == 1, "Salto ocioso inicial");
    }

    private static void testarMemoria() {
        Processo processo = processo("P", 0, 1, "MEM 0", "MEM 17", "MEM 0", "MEM 32", "MEM 0", "CPU 1");
        Simulador simulador = simular(configuracao("FCFS", 2, 0, 2), processo);
        verificar(simulador.memoria.faltas == 4 && simulador.memoria.acertos == 1 && simulador.memoria.referencias == 5, "FIFO não é LRU");
        verificar(objetos(simulador, "SUBSTITUICAO_FIFO").size() == 2, "Substituições FIFO");
        verificar(simulador.registro().stream().anyMatch(linha -> linha.contains("deslocamento=1; fisico=17")), "Tradução endereço");
        verificar(processo.tabelaPaginas.isEmpty(), "Liberação das páginas");
        rejeitar(() -> simulador.memoria.acessar(processo.threads.get(0), -1), "Endereço negativo");
        Processo compartilhado = processo("P", 0, 1, "MEM 0", "CPU 1");
        adicionarThread(compartilhado, "T2", "MEM 0", "CPU 1");
        Simulador simultaneo = simular(configuracao("FCFS", 2, 0, 1), compartilhado);
        verificar(simultaneo.memoria.faltas == 2 && objetos(simultaneo, "CARREGAMENTO_PAGINA").size() == 1, "Faltas concorrentes da mesma página");
        Simulador isolado = simular(configuracao("FCFS", 2, 0, 1), processo("A", 0, 1, "MEM 0", "CPU 1"), processo("B", 0, 1, "MEM 0", "CPU 1"));
        verificar(isolado.memoria.faltas == 2 && objetos(isolado, "CARREGAMENTO_PAGINA").size() == 2, "Espaços independentes");
    }

    private static void testarIo() {
        Processo processo = processo("P", 0, 1, "IO disco B", "CPU 1");
        adicionarThread(processo, "T2", "CPU 2");
        Simulador simulador = simular(configuracao("FCFS", 2, 0, 2), processo);
        verificar(processo.threads.get(1).fim == 3 && processo.fim == 5, "Outra thread progride durante E/S");
        verificar(processo.threads.get(0).cpu == 2 && simulador.metricas().discoOcupado() == 3, "Bloqueada não consome CPU");
        verificar(processo.threads.get(0).caixaEntrada.equals(List.of("disco:1:OK")), "Resultado entregue");
        Processo assincrono = processo("A", 0, 1, "IO terminal NB", "CPU 1");
        Simulador naoBloqueante = simular(configuracao("FCFS", 2, 0, 2), assincrono);
        verificar(assincrono.threads.get(0).fim == 2 && assincrono.fim == 3, "Processo aguarda pendência assíncrona");
        verificar(objetos(naoBloqueante, "BLOQUEIO").isEmpty(), "NB não bloqueia thread");
        Simulador fila = simular(configuracao("FCFS", 2, 0, 2), processo("A", 0, 1, "IO disco B", "CPU 1"), processo("B", 0, 1, "IO disco B", "CPU 1"));
        verificar(objetos(fila, "INTERRUPCAO_IO").equals(List.of("A/T1", "B/T1")), "FCFS do dispositivo");
        verificar(fila.metricas().discoOcupado() == 6, "Tempo ocupado da fila");
    }

    private static void testarArquivos() {
        Arquivos arquivos = new Arquivos();
        Processo processo = processo("A", 0, 1, "CPU 1");
        arquivos.criar("/d", true, "rw", 0);
        arquivos.criar("/d/a", false, "rw", 1);
        int descritor = arquivos.abrir(processo, "/d/a", "rw");
        verificar(descritor == 3, "Descritor local");
        arquivos.escrever(processo, descritor, "abcdefghijklmnopQRST", 2);
        rejeitar(() -> arquivos.remover("/d/a", 3), "Remoção de arquivo aberto");
        arquivos.fechar(processo, descritor);
        rejeitar(() -> arquivos.ler(processo, descritor, 1), "Arquivo fechado");
        int leitura = arquivos.abrir(processo, "/d/a", "r");
        verificar(arquivos.ler(processo, leitura, 16).equals("abcdefghijklmnop"), "Primeiro bloco");
        verificar(arquivos.ler(processo, leitura, 9).equals("QRST"), "Bloco encadeado");
        verificar(arquivos.ler(processo, leitura, 1).isEmpty(), "Fim de arquivo");
        rejeitar(() -> arquivos.escrever(processo, leitura, "x", 4), "Descritor somente leitura");
        verificar(arquivos.listar("/d").contains("tamanho=20"), "Metadados");
        arquivos.fechar(processo, leitura);
        int escrita = arquivos.abrir(processo, "/d/a", "w");
        rejeitar(() -> arquivos.escrever(processo, escrita, "x".repeat(2049), 5), "Disco cheio");
        arquivos.fechar(processo, escrita);
        int conferir = arquivos.abrir(processo, "/d/a", "r");
        verificar(arquivos.ler(processo, conferir, 100).equals("abcdefghijklmnopQRST"), "Escrita rejeitada é atômica");
        arquivos.fechar(processo, conferir);
        rejeitar(() -> arquivos.remover("/d", 5), "Diretório não vazio");
        arquivos.remover("/d/a", 6);
        arquivos.remover("/d", 7);
        rejeitar(() -> arquivos.remover("/ausente", 8), "Caminho inexistente");
        arquivos.criar("/restrito", false, "r", 9);
        rejeitar(() -> arquivos.abrir(processo, "/restrito", "w"), "Permissão do nó");
        rejeitar(() -> Arquivos.validarCaminho("/a/../b"), "Travessia ambígua");
        Processo outro = processo("B", 0, 1, "CPU 1");
        verificar(arquivos.abrir(outro, "/restrito", "r") == 3, "Descritores independentes entre processos");
        rejeitar(() -> arquivos.ler(processo, 3, 1), "Descritor de outro processo");
    }

    private static void testarCarga() throws IOException {
        rejeitar(() -> Configuracao.ler(new String[]{"--carga", "x", "--quantum", "0"}), "Quantum zero");
        rejeitar(() -> Configuracao.ler(new String[]{"--carga", "x", "--politica", "LRU"}), "Política inválida");
        rejeitar(() -> Configuracao.ler(new String[]{"--carga", "x", "--carga", "y"}), "Opção duplicada");
        rejeitar(() -> Carga.separar("ESCREVER 3 \"sem fim"), "Aspas incompletas");
        Processo fora = processo("A", 0, 1, "MEM 128");
        rejeitar(() -> Main.validarEnderecos(List.of(fora), 16), "Endereço excede espaço lógico");
        Path temporario = Files.createTempFile("carga-invalida-", ".txt");
        try {
            for (String carga : List.of("", "PROCESSO P 0 1 1\n", "CPU 1\n", "PROCESSO P 0 1 1\nTHREAD T\nCPU -1\nFIM_THREAD\nFIM_PROCESSO")) {
                Files.writeString(temporario, carga);
                boolean recusada = false;
                try { Carga.ler(temporario); } catch (IllegalArgumentException esperado) { recusada = true; }
                verificar(recusada, "Carga inválida recusada");
            }
        } finally { Files.deleteIfExists(temporario); }
    }

    private static void testarIntegracao() throws IOException {
        for (String carga : List.of("cpu", "io", "mista", "memoria", "arquivos", "threads-io", "verificacao")) {
            for (String politica : List.of("FCFS", "RR", "PRIORIDADE")) {
                Configuracao configuracao = configuracao(politica, 2, 1, 2);
                List<Processo> processos = Carga.ler(Path.of("cargas", carga + ".txt"));
                Simulador primeiro = new Simulador(configuracao, processos);
                primeiro.simular();
                Simulador segundo = new Simulador(configuracao, Carga.ler(Path.of("cargas", carga + ".txt")));
                segundo.simular();
                verificar(primeiro.registro().equals(segundo.registro()), "Determinismo: " + carga + "/" + politica);
                verificar(primeiro.metricas().resumoCsv().equals(segundo.metricas().resumoCsv()), "Métricas determinísticas");
                verificar(primeiro.metricas().errosOperacao() == 0, "Integração sem erro: " + carga);
                verificar(primeiro.metricas().cpuUtil() + primeiro.metricas().sobrecarga() <= primeiro.clock(), "Conservação do tempo");
                for (Processo processo : processos) {
                    verificar(processo.estado() == Estado.FINALIZADO && processo.arquivosAbertos.isEmpty(), "Recursos liberados");
                }
            }
        }
        Simulador erros = new Simulador(configuracao("FCFS", 2, 0, 2), Carga.ler(Path.of("cargas/erros-arquivos.txt")));
        erros.simular();
        verificar(erros.metricas().errosOperacao() == 4, "Erros simulados registrados sem abortar núcleo");
    }
}
