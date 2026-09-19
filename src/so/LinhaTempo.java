package so;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import javax.swing.JPanel;

/** Projeção do log: cada INSTRUCAO representa a unidade útil [clock-1, clock]. */
final class LinhaTempo extends JPanel {
    private static final long serialVersionUID = 1L;
    private record Intervalo(long inicio, long fim, String objeto) { }
    private final List<Intervalo> intervalos = new ArrayList<>();
    private final Map<String, Integer> linhas = new LinkedHashMap<>();
    private final long total;

    LinhaTempo(List<String> registro, long total) {
        this.total = total;
        linhas.put("Contexto", 0);
        long inicioTroca = 0;
        for (String evento : registro) {
            String[] campos = evento.split(" \\| ", 4);
            long instante = Long.parseLong(campos[0]);
            if (campos[1].equals("INICIO_TROCA")) { inicioTroca = instante; }
            if (campos[1].equals("FIM_TROCA") && instante > inicioTroca) {
                intervalos.add(new Intervalo(inicioTroca, instante, "Contexto"));
            }
            if (campos[1].equals("INSTRUCAO")) {
                linhas.putIfAbsent(campos[2], linhas.size());
                intervalos.add(new Intervalo(instante - 1, instante, campos[2]));
            }
        }
        setBackground(new Color(255, 255, 245));
        setPreferredSize(new Dimension(900, Math.max(360, linhas.size() * 54 + 100)));
    }

    @Override protected void paintComponent(Graphics desenho) {
        super.paintComponent(desenho);
        int largura = Math.max(1, getWidth() - 165);
        desenho.setColor(Color.DARK_GRAY);
        desenho.drawString("CPU • execução concluída | barras = trabalho útil; cinza = troca; vazios = sem uso desta linha", 20, 24);
        for (Map.Entry<String, Integer> linha : linhas.entrySet()) {
            int y = 65 + linha.getValue() * 54;
            desenho.setColor(new Color(224, 225, 215));
            desenho.fillRect(125, y, largura, 28);
            desenho.setColor(Color.DARK_GRAY);
            desenho.drawString(linha.getKey(), 18, y + 19);
        }
        for (Intervalo intervalo : intervalos) {
            int linha = linhas.get(intervalo.objeto());
            int x = 125 + (int) (intervalo.inicio() * (double) largura / Math.max(1, total));
            int fim = 125 + (int) (intervalo.fim() * (double) largura / Math.max(1, total));
            desenho.setColor(linha == 0 ? Color.GRAY : Color.getHSBColor((linha * 0.17f) % 1, 0.65f, 0.64f));
            desenho.fillRect(x, 65 + linha * 54, Math.max(1, fim - x), 28);
        }
        desenho.setColor(Color.DARK_GRAY);
        for (int marca = 0; marca <= 10; marca++) {
            int x = 125 + largura * marca / 10;
            desenho.drawString("" + Math.round(total * (double) marca / 10), x - 4, 52);
        }
    }
}
