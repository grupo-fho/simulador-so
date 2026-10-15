package so;

import java.awt.Component;
import java.awt.Container;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.concurrent.atomic.AtomicBoolean;
import javax.imageio.ImageIO;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.SwingUtilities;

/** Testa a apresentação offscreen; não substitui a conferência nativa no Windows. */
public final class TestesInterface {
    private TestesInterface() { }

    public static void main(String[] argumentos) throws Exception {
        Path temporario = Files.createTempDirectory("so-interface-");
        try {
            Files.createDirectories(temporario.resolve("cargas"));
            Files.copy(Path.of("cargas/mista.txt"), temporario.resolve("cargas/mista.txt"));
            InterfaceGrafica[] interfaceGrafica = new InterfaceGrafica[1];
            SwingUtilities.invokeAndWait(() -> {
                InterfaceGrafica.configurarAparencia();
                interfaceGrafica[0] = new InterfaceGrafica(temporario);
                interfaceGrafica[0].painel().setSize(1180, 760);
                organizar(interfaceGrafica[0].painel());
                if (argumentos.length == 1) { capturar(interfaceGrafica[0], Path.of(argumentos[0] + "-configuracao.png")); }
                JButton executar = encontrarExecucao(interfaceGrafica[0].painel());
                if (executar == null) { throw new AssertionError("Botão de execução ausente."); }
                executar.doClick();
                if (executar.isEnabled()) { throw new AssertionError("Deveria bloquear execução duplicada."); }
            });
            AtomicBoolean ocupada = new AtomicBoolean(true);
            long limite = System.nanoTime() + 20_000_000_000L;
            while (ocupada.get() && System.nanoTime() < limite) {
                Thread.sleep(20);
                SwingUtilities.invokeAndWait(() -> ocupada.set(interfaceGrafica[0].ocupada()));
            }
            if (ocupada.get()) { throw new AssertionError("Timeout na execução gráfica."); }
            Path saida = interfaceGrafica[0].ultimaSaida();
            if (saida == null) { throw new AssertionError("Interface não publicou os resultados."); }
            Configuracao configuracao = Configuracao.ler(new String[]{"--carga", temporario.resolve("cargas/mista.txt").toString(),
                    "--saida", temporario.resolve("referencia").toString()});
            Main.executar(configuracao);
            for (String arquivo : new String[]{"resumo.csv", "threads.csv", "processos.csv"}) {
                if (!Files.readString(saida.resolve(arquivo)).equals(Files.readString(configuracao.saida().resolve(arquivo)))) {
                    throw new AssertionError("GUI diverge da CLI: " + arquivo);
                }
            }
            SwingUtilities.invokeAndWait(() -> {
                if (!encontrarExecucao(interfaceGrafica[0].painel()).isEnabled()) { throw new AssertionError("Botão não reativado."); }
                organizar(interfaceGrafica[0].painel());
                if (argumentos.length == 1) { capturar(interfaceGrafica[0], Path.of(argumentos[0] + "-resultados.png")); }
            });
            testarPassos(temporario, configuracao.saida(), argumentos);
            SwingUtilities.invokeAndWait(() -> {
                JButton atalhoDoom = encontrarBotao(interfaceGrafica[0].painel(), "DOOM clássico");
                if (atalhoDoom == null) { throw new AssertionError("Atalho DOOM ausente."); }
                atalhoDoom.doClick();
                organizar(interfaceGrafica[0].painel());
                if (encontrarBotao(interfaceGrafica[0].painel(), "Jogar DOOM") == null) {
                    throw new AssertionError("Central de jogos não abriu.");
                }
                if (argumentos.length == 1) { capturar(interfaceGrafica[0], Path.of(argumentos[0] + "-doom.png")); }
            });
            System.out.println("OK: interface executa a carga, evita duplicação e reproduz as métricas da CLI.");
        } finally {
            try (java.util.stream.Stream<Path> arquivos = Files.walk(temporario)) {
                for (Path arquivo : arquivos.sorted(Comparator.reverseOrder()).toList()) { Files.delete(arquivo); }
            }
        }
    }

    private static void testarPassos(Path raiz, Path referencia, String[] argumentos) throws Exception {
        InterfaceGrafica[] gui = new InterfaceGrafica[1];
        SwingUtilities.invokeAndWait(() -> {
            gui[0] = new InterfaceGrafica(raiz);
            gui[0].painel().setSize(1180, 760);
            selecionarPassos(gui[0].painel());
            encontrarExecucao(gui[0].painel()).doClick();
        });
        esperar(() -> encontrarBotao(gui[0].painel(), "Próximo passo").isEnabled());
        SwingUtilities.invokeAndWait(() -> {
            if (!gui[0].ocupada() || encontrarExecucao(gui[0].painel()).isEnabled()) {
                throw new AssertionError("Sessão pausada deve impedir outra execução.");
            }
            encontrarBotao(gui[0].painel(), "Próximo passo").doClick();
            encontrarBotao(gui[0].painel(), "Continuar").doClick();
        });
        // Deixa o temporizador executar antes de testar a pausa.
        esperar(() -> gui[0].clockAtual() > 0);
        long[] clockPausado = new long[1];
        SwingUtilities.invokeAndWait(() -> {
            encontrarBotao(gui[0].painel(), "Pausar").doClick();
            clockPausado[0] = gui[0].clockAtual();
            if (argumentos.length == 1) {
                organizar(gui[0].painel());
                capturar(gui[0], Path.of(argumentos[0] + "-pausa.png"));
            }
        });
        Thread.sleep(500);
        SwingUtilities.invokeAndWait(() -> {
            if (clockPausado[0] != gui[0].clockAtual()) { throw new AssertionError("Clock avançou durante pausa."); }
            encontrarBotao(gui[0].painel(), "Próximo passo").doClick();
            if (gui[0].clockAtual() <= clockPausado[0]) { throw new AssertionError("Passo não avançou."); }
            encontrarBotao(gui[0].painel(), "Continuar").doClick();
        });
        esperar(() -> !gui[0].ocupada());
        for (String arquivo : new String[]{"resumo.csv", "threads.csv", "processos.csv"}) {
            if (!Files.readString(gui[0].ultimaSaida().resolve(arquivo)).equals(Files.readString(referencia.resolve(arquivo)))) {
                throw new AssertionError("Execução pausada diverge da CLI: " + arquivo);
            }
        }
        SwingUtilities.invokeAndWait(() -> {
            if (encontrarBotao(gui[0].painel(), "Próximo passo").isEnabled()
                    || encontrarBotao(gui[0].painel(), "Continuar").isEnabled()) {
                throw new AssertionError("Controles ativos após conclusão.");
            }
        });
        System.out.println("OK: passo, avanço automático, pausa e retomada preservam os resultados da CLI.");
    }

    private static void esperar(java.util.function.BooleanSupplier condicao) throws Exception {
        AtomicBoolean pronta = new AtomicBoolean(false);
        long limite = System.nanoTime() + 30_000_000_000L;
        while (!pronta.get() && System.nanoTime() < limite) {
            SwingUtilities.invokeAndWait(() -> pronta.set(condicao.getAsBoolean()));
            if (!pronta.get()) { Thread.sleep(20); }
        }
        if (!pronta.get()) { throw new AssertionError("Timeout aguardando controle de execução."); }
    }

    private static void selecionarPassos(Container container) {
        for (Component componente : container.getComponents()) {
            if (componente instanceof JCheckBox caixa && caixa.getText().equals("Passo a passo")) { caixa.setSelected(true); }
            if (componente instanceof Container filho) { selecionarPassos(filho); }
        }
    }

    private static JButton encontrarExecucao(Container container) {
        return encontrarBotao(container, "Executar simulação");
    }

    private static JButton encontrarBotao(Container container, String texto) {
        for (Component componente : container.getComponents()) {
            if (componente instanceof JButton botao && botao.getText() != null && botao.getText().contains(texto)) { return botao; }
            if (componente instanceof Container filho) {
                JButton encontrado = encontrarBotao(filho, texto);
                if (encontrado != null) { return encontrado; }
            }
        }
        return null;
    }

    private static void organizar(Container container) {
        container.doLayout();
        for (Component componente : container.getComponents()) {
            if (componente instanceof Container filho) { organizar(filho); }
        }
    }

    private static void capturar(InterfaceGrafica interfaceGrafica, Path caminho) {
        BufferedImage imagem = new BufferedImage(1180, 760, BufferedImage.TYPE_INT_RGB);
        Graphics2D desenho = imagem.createGraphics();
        interfaceGrafica.painel().printAll(desenho);
        desenho.dispose();
        try { ImageIO.write(imagem, "png", caminho.toFile()); }
        catch (IOException erro) { throw new IllegalStateException("Não foi possível gravar a prévia.", erro); }
    }
}
