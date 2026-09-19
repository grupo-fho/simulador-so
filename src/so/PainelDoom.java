package so;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Desktop;
import java.awt.Font;
import java.awt.GridLayout;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.ExecutionException;
import javax.swing.*;

/** Seleção explícita do motor e dos dados do jogo, sem comandos de shell. */
final class PainelDoom extends JPanel {
    private static final long serialVersionUID = 1L;
    private final Doom doom = new Doom();
    private final JTextField motor = new JTextField();
    private final JTextField wad = new JTextField();
    private final JTextField mod = new JTextField();
    private final JButton jogar = new JButton("▶  Jogar DOOM");
    private final JLabel estado = new JLabel("Selecione o motor e o WAD para começar.");
    private final Path dados = Path.of(System.getProperty("user.home"), ".simulador-so", "doom");

    PainelDoom(Path raiz) {
        super(new BorderLayout(12, 18));
        setBorder(BorderFactory.createEmptyBorder(20, 22, 20, 22));
        JPanel cabecalho = new JPanel(new GridLayout(0, 1, 0, 8));
        JLabel titulo = new JLabel("D O O M", TemaAero.icone("DOOM"), SwingConstants.LEFT);
        titulo.setFont(new Font("SansSerif", Font.BOLD, 34));
        titulo.setForeground(new Color(126, 60, 18));
        cabecalho.add(titulo);
        cabecalho.add(new JLabel("O clássico de 1993 • Chocolate Doom • execução local"));
        add(cabecalho, BorderLayout.NORTH);
        JPanel campos = new JPanel(new GridLayout(0, 1, 0, 9));
        campos.add(new JLabel("1. Executável do Chocolate Doom (mantenha as DLLs ao lado dele)"));
        campos.add(seletor(motor));
        campos.add(new JLabel("2. IWAD do jogo: DOOM.WAD, DOOM1.WAD ou DOOM2.WAD"));
        campos.add(seletor(wad));
        campos.add(new JLabel("3. Mapas opcionais (PWAD); apague o campo para jogar o original"));
        campos.add(seletor(mod));
        campos.add(new JLabel("24TIMEBOM exige DOOM.WAD completo; não funciona com o shareware."));
        campos.add(new JLabel("Abre em tela cheia. As métricas da simulação não incluem o jogo."));
        campos.add(new JLabel("Controles padrão: setas • Ctrl atira • Espaço abre portas • Esc abre o menu"));
        add(campos, BorderLayout.CENTER);
        JPanel rodape = new JPanel(new BorderLayout(8, 10));
        rodape.add(estado, BorderLayout.NORTH);
        jogar.addActionListener(evento -> iniciar());
        rodape.add(jogar, BorderLayout.EAST);
        JButton abrirLog = new JButton("Abrir log do jogo");
        abrirLog.addActionListener(evento -> abrirLog());
        rodape.add(abrirLog, BorderLayout.WEST);
        add(rodape, BorderLayout.SOUTH);
        Path pasta = raiz.resolve("jogos/doom");
        String executavel = System.getProperty("os.name").startsWith("Windows") ? "chocolate-doom.exe" : "chocolate-doom";
        motor.setText(pasta.resolve(executavel).toString());
        wad.setText(pasta.resolve("doom2.wad").toString());
        for (String nome : new String[]{"doom2.wad", "DOOM2.WAD", "doom.wad", "DOOM.WAD", "doom1.wad", "DOOM1.WAD"}) {
            if (Files.isRegularFile(pasta.resolve(nome))) { wad.setText(pasta.resolve(nome).toString()); break; }
        }
        if (!Files.isRegularFile(Path.of(wad.getText()))) {
            estado.setText("Falta o IWAD base. Selecione seu DOOM.WAD para jogar.");
        }
        if (Files.isRegularFile(Path.of(motor.getText())) && Files.isRegularFile(Path.of(wad.getText()))) {
            estado.setText("Arquivos locais encontrados. Pronto para jogar.");
        }
    }

    private JPanel seletor(JTextField campo) {
        JPanel linha = new JPanel(new BorderLayout(8, 0));
        linha.add(campo, BorderLayout.CENTER);
        JButton procurar = new JButton("Procurar…");
        procurar.addActionListener(evento -> {
            JFileChooser seletor = new JFileChooser();
            if (seletor.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
                campo.setText(seletor.getSelectedFile().getAbsolutePath());
            }
        });
        linha.add(procurar, BorderLayout.EAST);
        return linha;
    }

    private void iniciar() {
        jogar.setEnabled(false);
        estado.setText("Iniciando DOOM…");
        String caminhoMotor = motor.getText().strip();
        String caminhoWad = wad.getText().strip();
        String caminhoMod = mod.getText().strip();
        new SwingWorker<Integer, Void>() {
            @Override protected Integer doInBackground() throws IOException, InterruptedException {
                Process processo = doom.iniciar(Path.of(caminhoMotor), Path.of(caminhoWad),
                        caminhoMod.isEmpty() ? null : Path.of(caminhoMod), dados);
                SwingUtilities.invokeLater(() -> estado.setText("DOOM em execução • feche o jogo pelo menu Esc / Quit."));
                return processo.waitFor();
            }
            @Override protected void done() {
                jogar.setEnabled(true);
                try {
                    int codigo = get();
                    estado.setText(codigo == 0 ? "Jogo encerrado. Você pode jogar novamente." : "O motor terminou com erro " + codigo + ". Consulte o log.");
                } catch (InterruptedException erro) {
                    Thread.currentThread().interrupt();
                    estado.setText("Espera interrompida.");
                } catch (ExecutionException erro) {
                    estado.setText("Não foi possível iniciar o jogo.");
                    JOptionPane.showMessageDialog(PainelDoom.this, erro.getCause().getMessage(), "DOOM", JOptionPane.ERROR_MESSAGE);
                }
            }
        }.execute();
    }

    private void abrirLog() {
        try {
            if (doom.log() == null) { throw new IOException("Ainda não há log: inicie o jogo primeiro."); }
            if (!Desktop.isDesktopSupported() || !Desktop.getDesktop().isSupported(Desktop.Action.OPEN)) {
                throw new IOException("Abra o log em: " + doom.log());
            }
            Desktop.getDesktop().open(doom.log().toFile());
        } catch (IOException | UnsupportedOperationException erro) {
            JOptionPane.showMessageDialog(this, erro.getMessage(), "Log do DOOM", JOptionPane.INFORMATION_MESSAGE);
        }
    }
}
