package so;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Desktop;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.GridLayout;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.beans.PropertyVetoException;
import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JDesktopPane;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JInternalFrame;
import javax.swing.JLabel;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.JProgressBar;
import javax.swing.JScrollPane;
import javax.swing.JSpinner;
import javax.swing.JTabbedPane;
import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.SpinnerNumberModel;
import javax.swing.SwingUtilities;
import javax.swing.SwingWorker;
import javax.swing.table.DefaultTableModel;

/** Desktop didático: somente a apresentação usa threads reais (SwingWorker). */
public final class InterfaceGrafica {
    private final Path raiz;
    private final JPanel painel = new JPanel(new BorderLayout());
    private final JDesktopPane desktop = TemaAero.desktop();
    private final JInternalFrame configuracao = janela("Configuração da simulação", 185, 62, 740, 575);
    private final JInternalFrame resultados = janela("Monitor do sistema", 230, 92, 800, 570);
    private final JTextField carga = new JTextField();
    private final JTextField pastaSaida = new JTextField();
    private final JComboBox<String> politica = new JComboBox<>(new String[]{"FCFS", "RR", "PRIORIDADE"});
    private final Map<String, JSpinner> parametros = new LinkedHashMap<>();
    private final JTextField semente = new JTextField("42");
    private final JButton executar = new JButton("▶  Executar simulação");
    private final JLabel status = new JLabel(" Pronto • selecione uma carga e execute");
    private final JLabel clock = new JLabel(" Clock lógico: — ");
    private final JProgressBar progresso = new JProgressBar();
    private final JTabbedPane abasResultados = new JTabbedPane();
    private boolean ocupada;
    private Path ultimaSaida;

    public static void main(String[] argumentos) {
        SwingUtilities.invokeLater(() -> {
            configurarAparencia();
            InterfaceGrafica interfaceGrafica = new InterfaceGrafica(localizarRaiz());
            JFrame janela = new JFrame("Simulador SO • Frutiger Aero");
            janela.setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
            janela.addWindowListener(new WindowAdapter() {
                @Override public void windowClosing(WindowEvent evento) {
                    if (interfaceGrafica.ocupada) {
                        JOptionPane.showMessageDialog(janela, "Aguarde a conclusão da simulação antes de sair.");
                    } else { janela.dispose(); }
                }
            });
            janela.setContentPane(interfaceGrafica.painel);
            janela.setSize(1180, 790);
            janela.setMinimumSize(new Dimension(1050, 740));
            janela.setLocationRelativeTo(null);
            janela.setVisible(true);
        });
    }

    static void configurarAparencia() {
        TemaAero.configurar();
    }

    InterfaceGrafica(Path raiz) {
        this.raiz = raiz;
        carga.setText(raiz.resolve("cargas/mista.txt").toString());
        pastaSaida.setText(raiz.resolve("resultados").toString());
        desktop.setBackground(new Color(0, 112, 116));
        painel.add(desktop, BorderLayout.CENTER);
        JPanel topo = new JPanel(new BorderLayout());
        topo.setBackground(new Color(23, 105, 155));
        topo.setBorder(BorderFactory.createEmptyBorder(9, 16, 9, 16));
        JLabel titulo = new JLabel("SO / LAB     •     FRUTIGER AERO");
        titulo.setForeground(Color.WHITE);
        titulo.setFont(new Font("Dialog", Font.BOLD, 14));
        JLabel descricao = new JLabel("Eventos discretos  /  uma CPU  /  tempo lógico");
        descricao.setForeground(new Color(217, 246, 255));
        topo.add(titulo, BorderLayout.WEST);
        topo.add(descricao, BorderLayout.EAST);
        painel.add(topo, BorderLayout.NORTH);
        criarAtalho("Meu simulador", "CPU", 30, () -> mostrar(configuracao));
        criarAtalho("Monitor do sistema", "SYS", 140, () -> mostrar(resultados));
        criarAtalho("Cargas de trabalho", "TXT", 250, this::escolherCarga);
        criarAtalho("Resultados", "LOG", 360, this::abrirPasta);
        criarAtalho("DOOM clássico", "DOOM", 470, this::mostrarDoom);
        configurarFormulario();
        resultados.setContentPane(abasResultados);
        JTextArea vazio = areaTexto("MONITOR DO SISTEMA\n\nExecute uma simulação para consultar:\n\n• Resumo de métricas\n• Processos e threads\n• Linha do tempo da CPU\n• Registro completo dos eventos\n\nOs resultados são calculados pelo mesmo núcleo da CLI.");
        abasResultados.addTab("Bem-vindo", new JScrollPane(vazio));
        desktop.add(configuracao);
        desktop.add(resultados);
        painel.add(criarBarraTarefas(), BorderLayout.SOUTH);
        mostrar(configuracao);
    }

    private static JInternalFrame janela(String titulo, int x, int y, int largura, int altura) {
        JInternalFrame janela = new JInternalFrame(titulo, true, true, true, true);
        janela.setDefaultCloseOperation(JInternalFrame.HIDE_ON_CLOSE);
        janela.setBounds(x, y, largura, altura);
        return janela;
    }

    private void criarAtalho(String nome, String sigla, int y, Runnable acao) {
        JButton atalho = new JButton(TemaAero.icone(sigla));
        atalho.setText(nome);
        atalho.setHorizontalTextPosition(JButton.CENTER);
        atalho.setVerticalTextPosition(JButton.BOTTOM);
        atalho.setForeground(Color.WHITE);
        atalho.setContentAreaFilled(false);
        atalho.setBorderPainted(false);
        atalho.setBounds(10, y, 164, 88);
        atalho.addActionListener(evento -> acao.run());
        desktop.add(atalho);
    }

    private JPanel criarBarraTarefas() {
        JPanel barra = new JPanel(new BorderLayout(8, 0)) {
            private static final long serialVersionUID = 1L;
            @Override protected void paintComponent(Graphics desenho) {
                TemaAero.vidro(desenho, getWidth(), getHeight());
            }
        };
        barra.setBorder(BorderFactory.createCompoundBorder(BorderFactory.createRaisedBevelBorder(), BorderFactory.createEmptyBorder(5, 5, 5, 5)));
        JPanel tarefas = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 0));
        tarefas.setOpaque(false);
        JButton iniciar = new JButton("◉  Iniciar");
        iniciar.setFont(iniciar.getFont().deriveFont(Font.BOLD));
        JPopupMenu menu = new JPopupMenu();
        adicionarMenu(menu, "Configurar simulação", () -> mostrar(configuracao));
        adicionarMenu(menu, "Monitor do sistema", () -> mostrar(resultados));
        adicionarMenu(menu, "Abrir resultados", this::abrirPasta);
        adicionarMenu(menu, "DOOM clássico", this::mostrarDoom);
        adicionarMenu(menu, "Ajuda", this::mostrarAjuda);
        iniciar.addActionListener(evento -> menu.show(iniciar, 0, -menu.getPreferredSize().height));
        tarefas.add(iniciar);
        tarefas.add(botao("Configuração", () -> mostrar(configuracao)));
        tarefas.add(botao("Monitor", () -> mostrar(resultados)));
        barra.add(tarefas, BorderLayout.WEST);
        barra.add(status, BorderLayout.CENTER);
        clock.setBorder(BorderFactory.createLoweredBevelBorder());
        barra.add(clock, BorderLayout.EAST);
        return barra;
    }

    private static void adicionarMenu(JPopupMenu menu, String titulo, Runnable acao) {
        JMenuItem opcao = new JMenuItem(titulo);
        opcao.addActionListener(evento -> acao.run());
        menu.add(opcao);
    }

    private static JButton botao(String texto, Runnable acao) {
        JButton botao = new JButton(texto);
        botao.addActionListener(evento -> acao.run());
        return botao;
    }

    private void configurarFormulario() {
        JPanel conteudo = new JPanel(new BorderLayout(10, 10));
        conteudo.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));
        JPanel arquivos = new JPanel(new GridLayout(0, 1, 0, 5));
        arquivos.add(new JLabel("1. Carga externa de trabalho"));
        JPanel seletor = new JPanel(new BorderLayout(5, 0));
        seletor.add(carga, BorderLayout.CENTER);
        seletor.add(botao("Procurar...", this::escolherCarga), BorderLayout.EAST);
        arquivos.add(seletor);
        JPanel exemplos = new JPanel(new FlowLayout(FlowLayout.LEFT, 4, 0));
        for (String exemplo : List.of("mista", "cpu", "io", "memoria", "arquivos")) {
            exemplos.add(botao(exemplo + ".txt", () -> carga.setText(raiz.resolve("cargas/" + exemplo + ".txt").toString())));
        }
        exemplos.add(botao("Visualizar", this::visualizarCarga));
        arquivos.add(exemplos);
        conteudo.add(arquivos, BorderLayout.NORTH);

        JPanel parametrosPainel = new JPanel(new GridLayout(0, 2, 16, 8));
        parametrosPainel.setBorder(BorderFactory.createTitledBorder("2. CPU, memória e dispositivos"));
        parametrosPainel.add(campo("Política de CPU", politica));
        adicionarParametro(parametrosPainel, "quantum", "Quantum (Round Robin)", 3, 1);
        adicionarParametro(parametrosPainel, "troca", "Custo da troca de contexto", 1, 0);
        adicionarParametro(parametrosPainel, "pagina", "Tamanho da página", 16, 1);
        adicionarParametro(parametrosPainel, "molduras", "Molduras físicas", 4, 1);
        adicionarParametro(parametrosPainel, "falta", "Tempo de falta de página", 5, 1);
        adicionarParametro(parametrosPainel, "disco", "Tempo de serviço do disco", 4, 1);
        adicionarParametro(parametrosPainel, "terminal", "Tempo de serviço do terminal", 2, 1);
        parametrosPainel.add(campo("Semente (modelo sem sorteios)", semente));
        parametrosPainel.add(new JLabel("Prioridade: menor número vence."));
        politica.addActionListener(evento -> parametros.get("quantum").setEnabled("RR".equals(politica.getSelectedItem())));
        parametros.get("quantum").setEnabled(false);
        conteudo.add(parametrosPainel, BorderLayout.CENTER);

        JPanel rodape = new JPanel(new GridLayout(0, 1, 0, 5));
        rodape.add(new JLabel("3. Pasta de resultados — cada execução cria uma subpasta nova"));
        JPanel saida = new JPanel(new BorderLayout(5, 0));
        saida.add(pastaSaida, BorderLayout.CENTER);
        saida.add(botao("Alterar...", this::escolherSaida), BorderLayout.EAST);
        rodape.add(saida);
        JPanel acoes = new JPanel(new BorderLayout(8, 0));
        acoes.add(new JLabel("Clock lógico • sem espera em tempo real"), BorderLayout.WEST);
        executar.addActionListener(evento -> executarSimulacao());
        acoes.add(executar, BorderLayout.EAST);
        rodape.add(acoes);
        progresso.setStringPainted(true);
        progresso.setString("Pronto");
        rodape.add(progresso);
        conteudo.add(rodape, BorderLayout.SOUTH);
        configuracao.setContentPane(conteudo);
    }

    private static JPanel campo(String titulo, Component componente) {
        JPanel campo = new JPanel(new BorderLayout(0, 3));
        campo.add(new JLabel(titulo), BorderLayout.NORTH);
        campo.add(componente, BorderLayout.CENTER);
        return campo;
    }

    private void adicionarParametro(JPanel painel, String chave, String titulo, int valor, int minimo) {
        JSpinner spinner = new JSpinner(new SpinnerNumberModel(valor, minimo, 1_000_000, 1));
        parametros.put(chave, spinner);
        painel.add(campo(titulo, spinner));
    }

    private void escolherCarga() {
        JFileChooser seletor = new JFileChooser(raiz.resolve("cargas").toFile());
        if (seletor.showOpenDialog(painel) == JFileChooser.APPROVE_OPTION) {
            carga.setText(seletor.getSelectedFile().getAbsolutePath());
            mostrar(configuracao);
        }
    }

    private void escolherSaida() {
        JFileChooser seletor = new JFileChooser();
        seletor.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
        if (seletor.showSaveDialog(painel) == JFileChooser.APPROVE_OPTION) {
            pastaSaida.setText(seletor.getSelectedFile().getAbsolutePath());
        }
    }

    private void visualizarCarga() {
        try {
            Path caminho = Path.of(carga.getText().strip());
            if (Files.size(caminho) > 1_000_000) { throw new IOException("Prévia limitada a arquivos de até 1 MB."); }
            JInternalFrame previa = janela("Carga • " + caminho.getFileName(), 250, 85, 650, 530);
            previa.setContentPane(new JScrollPane(areaTexto(Files.readString(caminho))));
            previa.setDefaultCloseOperation(JInternalFrame.DISPOSE_ON_CLOSE);
            desktop.add(previa);
            mostrar(previa);
        } catch (IOException | IllegalArgumentException erro) { informarErro(erro); }
    }

    private void executarSimulacao() {
        if (ocupada) { return; }
        List<String> argumentos = new ArrayList<>(List.of("--carga", carga.getText().strip(), "--politica",
                politica.getSelectedItem().toString(), "--semente", semente.getText().strip()));
        Path pasta;
        try {
            pasta = Path.of(pastaSaida.getText().strip()).toAbsolutePath();
            for (Map.Entry<String, JSpinner> parametro : parametros.entrySet()) {
                parametro.getValue().commitEdit();
                argumentos.add("--" + parametro.getKey());
                argumentos.add(parametro.getValue().getValue().toString());
            }
            Configuracao.ler(argumentos.toArray(String[]::new));
        } catch (IllegalArgumentException | java.text.ParseException erro) { informarErro(erro); return; }
        ocupada = true;
        executar.setEnabled(false);
        progresso.setIndeterminate(true);
        progresso.setString("Executando e gravando resultados...");
        status.setText(" Simulação em andamento");
        new SwingWorker<Simulador, Void>() {
            private Path saida;
            @Override protected Simulador doInBackground() throws IOException {
                Configuracao validacao = Configuracao.ler(argumentos.toArray(String[]::new));
                Main.validarEnderecos(Carga.ler(validacao.carga()), validacao.pagina());
                Files.createDirectories(pasta);
                saida = Files.createTempDirectory(pasta, "execucao-");
                argumentos.addAll(List.of("--saida", saida.toString()));
                return Main.executar(Configuracao.ler(argumentos.toArray(String[]::new)));
            }
            @Override protected void done() {
                ocupada = false;
                executar.setEnabled(true);
                progresso.setIndeterminate(false);
                try {
                    Simulador simulador = get();
                    ultimaSaida = saida;
                    exibirResultados(simulador);
                    progresso.setString("Concluído • resultados gravados");
                    status.setText(" Concluído • clock " + simulador.clock());
                    clock.setText(" Clock lógico: " + simulador.clock() + " ");
                } catch (InterruptedException erro) {
                    Thread.currentThread().interrupt();
                    progresso.setString("Interrompido");
                    informarErro(erro);
                } catch (ExecutionException erro) {
                    progresso.setString("Falha • consulte a mensagem");
                    status.setText(" Falha na execução");
                    informarErro(erro.getCause());
                }
            }
        }.execute();
    }

    private void exibirResultados(Simulador simulador) {
        Metricas metricas = simulador.metricas();
        abasResultados.removeAll();
        JPanel resumo = new JPanel(new BorderLayout(12, 12));
        resumo.setBorder(BorderFactory.createEmptyBorder(16, 16, 16, 16));
        JPanel indicadores = new JPanel(new GridLayout(2, 3, 12, 12));
        indicadores.add(indicador("TEMPO TOTAL", "" + metricas.tempoTotal()));
        indicadores.add(indicador("CPU ÚTIL", "" + metricas.cpuUtil()));
        indicadores.add(indicador("SOBRECARGA", "" + metricas.sobrecarga()));
        indicadores.add(indicador("TROCAS", "" + metricas.trocas()));
        indicadores.add(indicador("FALTAS DE PÁGINA", "" + metricas.faltas()));
        indicadores.add(indicador("ERROS DE OPERAÇÃO", "" + metricas.errosOperacao()));
        resumo.add(indicadores, BorderLayout.NORTH);
        resumo.add(new JScrollPane(tabelaResumo(metricas.resumoCsv())), BorderLayout.CENTER);
        resumo.add(botao("Abrir pasta desta execução", this::abrirPasta), BorderLayout.SOUTH);
        abasResultados.addTab("Visão geral", resumo);
        abasResultados.addTab("Processos", new JScrollPane(tabelaCsv(metricas.processosCsv())));
        abasResultados.addTab("Threads", new JScrollPane(tabelaCsv(metricas.threadsCsv())));
        abasResultados.addTab("CPU / tempo", new JScrollPane(new LinhaTempo(simulador.registro(), simulador.clock())));
        abasResultados.addTab("Eventos", new JScrollPane(areaTexto(String.join("\n", simulador.registro()))));
        mostrar(resultados);
    }

    private static JPanel indicador(String titulo, String valor) {
        JPanel cartao = new JPanel(new BorderLayout(0, 6));
        cartao.setBackground(new Color(235, 250, 255));
        cartao.setBorder(BorderFactory.createCompoundBorder(BorderFactory.createLoweredBevelBorder(), BorderFactory.createEmptyBorder(10, 10, 10, 10)));
        cartao.add(new JLabel(titulo), BorderLayout.NORTH);
        JLabel numero = new JLabel(valor);
        numero.setFont(new Font("Monospaced", Font.BOLD, 25));
        numero.setForeground(new Color(17, 107, 162));
        cartao.add(numero, BorderLayout.CENTER);
        return cartao;
    }

    private static JTable tabelaResumo(String csv) {
        String[] linhas = csv.strip().split("\n");
        String[] nomes = linhas[0].split(",");
        String[] valores = linhas[1].split(",");
        DefaultTableModel modelo = modeloTabela(new String[]{"Métrica (proporções entre 0 e 1)", "Valor"});
        for (int indice = 0; indice < nomes.length; indice++) { modelo.addRow(new String[]{nomes[indice], valores[indice]}); }
        return configurarTabela(modelo);
    }

    private static JTable tabelaCsv(String csv) {
        String[] linhas = csv.strip().split("\n");
        DefaultTableModel modelo = modeloTabela(linhas[0].split(","));
        for (int indice = 1; indice < linhas.length; indice++) { modelo.addRow(linhas[indice].split(",")); }
        return configurarTabela(modelo);
    }

    private static DefaultTableModel modeloTabela(String[] colunas) {
        return new DefaultTableModel(colunas, 0) {
            private static final long serialVersionUID = 1L;
            @Override public boolean isCellEditable(int linha, int coluna) { return false; }
        };
    }

    private static JTable configurarTabela(DefaultTableModel modelo) {
        JTable tabela = new JTable(modelo);
        tabela.setRowHeight(25);
        tabela.setFillsViewportHeight(true);
        return tabela;
    }

    private static JTextArea areaTexto(String texto) {
        JTextArea area = new JTextArea(texto);
        area.setEditable(false);
        area.setFont(new Font("Monospaced", Font.PLAIN, 12));
        area.setBackground(new Color(249, 253, 255));
        area.setMargin(new java.awt.Insets(12, 12, 12, 12));
        area.setCaretPosition(0);
        return area;
    }

    private void abrirPasta() {
        try {
            Path destino = ultimaSaida == null ? Path.of(pastaSaida.getText().strip()) : ultimaSaida;
            Files.createDirectories(destino);
            if (!Desktop.isDesktopSupported() || !Desktop.getDesktop().isSupported(Desktop.Action.OPEN)) {
                throw new IOException("Abra manualmente a pasta: " + destino);
            }
            Desktop.getDesktop().open(destino.toFile());
        } catch (IOException | IllegalArgumentException | UnsupportedOperationException erro) { informarErro(erro); }
    }

    private void mostrarAjuda() {
        JOptionPane.showMessageDialog(painel,
                "1. Escolha uma carga ou use mista.txt.\n2. Ajuste a política e os parâmetros.\n3. Clique em Executar simulação.\n\n"
                + "O Monitor mostra métricas, processos, threads, CPU e eventos.\nCada execução salva logs e CSVs em uma pasta nova.\n"
                + "A linha do tempo representa a execução concluída; não é tempo real.\n\n"
                + "Visual Frutiger Aero, com organização em janelas.\nNão é KDE nem Windows: é a interface do simulador.", "Ajuda do simulador", JOptionPane.INFORMATION_MESSAGE);
    }

    private JInternalFrame janelaDoom;

    private void mostrarDoom() {
        if (janelaDoom == null) {
            janelaDoom = janela("DOOM clássico • Central de jogos", 225, 65, 780, 610);
            janelaDoom.setContentPane(new PainelDoom(raiz));
            desktop.add(janelaDoom);
        }
        mostrar(janelaDoom);
    }

    private void informarErro(Throwable erro) {
        JOptionPane.showMessageDialog(painel, erro.getMessage(), "Não foi possível concluir", JOptionPane.ERROR_MESSAGE);
    }

    private static void mostrar(JInternalFrame janela) {
        janela.setVisible(true);
        try { janela.setIcon(false); janela.setSelected(true); }
        catch (PropertyVetoException erro) { janela.toFront(); }
        janela.toFront();
    }

    static Path localizarRaiz() {
        Path atual = Path.of("").toAbsolutePath();
        String executavel = System.getProperty("jpackage.app-path");
        if (executavel != null) { atual = Path.of(executavel).toAbsolutePath().getParent(); }
        else {
            try { atual = Path.of(InterfaceGrafica.class.getProtectionDomain().getCodeSource().getLocation().toURI()).toAbsolutePath(); }
            catch (URISyntaxException erro) { return Path.of("").toAbsolutePath(); }
        }
        for (int nivel = 0; nivel < 6 && atual != null; nivel++, atual = atual.getParent()) {
            if (Files.isDirectory(atual.resolve("cargas"))) { return atual; }
        }
        return Path.of("").toAbsolutePath();
    }

    // Acesso de pacote para conferir o desktop e as ações em testes sem uma janela nativa.
    JPanel painel() { return painel; }
    boolean ocupada() { return ocupada; }
    Path ultimaSaida() { return ultimaSaida; }
}
