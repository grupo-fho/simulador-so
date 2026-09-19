package so;

import java.awt.*;
import java.awt.geom.Ellipse2D;
import javax.swing.*;

/** Desenhos vetoriais locais: nenhuma imagem ou fonte precisa ser baixada. */
final class TemaAero {
    private TemaAero() { }

    static void configurar() {
        try { UIManager.setLookAndFeel(new javax.swing.plaf.nimbus.NimbusLookAndFeel()); }
        catch (UnsupportedLookAndFeelException erro) {
            throw new IllegalStateException("Não foi possível iniciar o tema Aero.", erro);
        }
        UIManager.put("control", new Color(229, 244, 251));
        UIManager.put("nimbusBase", new Color(36, 113, 160));
        UIManager.put("nimbusBlueGrey", new Color(177, 213, 232));
        UIManager.put("nimbusFocus", new Color(67, 183, 232));
        UIManager.put("text", new Color(22, 57, 78));
        for (Object chave : UIManager.getDefaults().keySet().toArray()) {
            if (chave.toString().endsWith(".font")) {
                UIManager.put(chave, new Font("SansSerif", Font.PLAIN, 12));
            }
        }
    }

    static void vidro(Graphics desenho, int largura, int altura) {
        Graphics2D pincel = (Graphics2D) desenho.create();
        pincel.setPaint(new GradientPaint(0, 0, new Color(196, 238, 255), 0, altura, new Color(41, 141, 197)));
        pincel.fillRect(0, 0, largura, altura);
        pincel.setColor(new Color(255, 255, 255, 95));
        pincel.fillRect(0, 0, largura, altura / 2);
        pincel.setColor(new Color(255, 255, 255, 190));
        pincel.drawLine(0, 0, largura, 0);
        pincel.dispose();
    }

    static JDesktopPane desktop() {
        return new JDesktopPane() {
            private static final long serialVersionUID = 1L;
            @Override protected void paintComponent(Graphics desenho) {
                super.paintComponent(desenho);
                Graphics2D pincel = (Graphics2D) desenho.create();
                pincel.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                int largura = getWidth();
                int altura = getHeight();
                pincel.setPaint(new GradientPaint(0, 0, new Color(0, 110, 190), 0, altura, new Color(132, 236, 242)));
                pincel.fillRect(0, 0, largura, altura);
                pincel.setPaint(new RadialGradientPaint(largura * .80f, altura * .18f,
                        Math.max(1, largura * .43f), new float[]{0, 1},
                        new Color[]{new Color(255, 255, 235, 230), new Color(255, 255, 255, 0)}));
                pincel.fillRect(0, 0, largura, altura);
                pincel.setColor(new Color(255, 255, 255, 65));
                pincel.fillOval(largura / 3, altura / 8, largura / 2, 45);
                pincel.fillOval(largura / 2, altura / 8 - 15, largura / 4, 65);
                pincel.setPaint(new GradientPaint(0, altura * .68f, new Color(168, 223, 50), 0, altura, new Color(35, 127, 37)));
                pincel.fillOval(-largura / 3, altura * 3 / 4, largura * 2, altura);
                pincel.setPaint(new GradientPaint(0, altura * .80f, new Color(96, 198, 48), 0, altura, new Color(20, 106, 50)));
                pincel.fillOval(-largura / 2, altura * 4 / 5, largura * 3 / 2, altura);
                for (int indice = 0; indice < 8; indice++) {
                    int tamanho = 24 + indice * 9;
                    int x = largura - 60 - (indice % 3) * 67;
                    int y = 85 + indice * 60;
                    pincel.setColor(new Color(230, 255, 255, 35));
                    pincel.fillOval(x, y, tamanho, tamanho);
                    pincel.setColor(new Color(255, 255, 255, 115));
                    pincel.drawOval(x, y, tamanho, tamanho);
                    pincel.drawArc(x + 4, y + 4, tamanho - 8, tamanho - 8, 45, 80);
                }
                pincel.setColor(new Color(255, 255, 255, 210));
                pincel.setFont(new Font("SansSerif", Font.PLAIN, 27));
                pincel.drawString("aero", largura - 123, altura - 48);
                pincel.setFont(new Font("SansSerif", Font.PLAIN, 11));
                pincel.drawString("SO / LAB", largura - 118, altura - 29);
                pincel.dispose();
            }
        };
    }

    static Icon icone(String sigla) {
        return new Icon() {
            public int getIconWidth() { return 56; }
            public int getIconHeight() { return 54; }
            public void paintIcon(Component componente, Graphics desenho, int x, int y) {
                Graphics2D pincel = (Graphics2D) desenho.create();
                pincel.translate(x, y);
                pincel.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                pincel.setColor(new Color(0, 47, 81, 65));
                pincel.fillOval(5, 45, 46, 8);
                Color base = sigla.equals("DOOM") ? new Color(176, 66, 26) : new Color(0, 128, 205);
                if (sigla.equals("TXT")) { base = new Color(68, 164, 39); }
                pincel.setPaint(new GradientPaint(0, 2, new Color(209, 255, 252), 0, 49, base));
                pincel.fillRoundRect(4, 1, 48, 48, 18, 18);
                pincel.setColor(new Color(255, 255, 255, 195));
                pincel.drawRoundRect(4, 1, 48, 48, 18, 18);
                pincel.setColor(new Color(255, 255, 255, 125));
                pincel.fill(new Ellipse2D.Double(10, 4, 36, 18));
                pincel.setFont(new Font("SansSerif", Font.BOLD, sigla.length() > 3 ? 11 : 13));
                int textoX = (56 - pincel.getFontMetrics().stringWidth(sigla)) / 2;
                pincel.setColor(new Color(7, 58, 91));
                pincel.drawString(sigla, textoX, 33);
                pincel.dispose();
            }
        };
    }
}
