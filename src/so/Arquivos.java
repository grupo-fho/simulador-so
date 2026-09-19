package so;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

final class Arquivos {
    private static final int TAMANHO_BLOCO = 16;
    private static final int TOTAL_BLOCOS = 128;
    private static final class No {
        final String nome;
        final boolean diretorio;
        final String permissoes;
        final long criacao;
        long modificacao;
        int tamanho;
        int primeiroBloco = -1;
        final Map<String, No> filhos = new TreeMap<>();
        No(String nome, boolean diretorio, String permissoes, long clock) {
            this.nome = nome;
            this.diretorio = diretorio;
            this.permissoes = permissoes;
            criacao = clock;
            modificacao = clock;
        }
    }
    private record Bloco(String conteudo, int proximo) { }
    private static final class Abertura {
        final No arquivo;
        final String modo;
        int posicao;
        Abertura(No arquivo, String modo) { this.arquivo = arquivo; this.modo = modo; }
    }
    private final No raiz = new No("/", true, "rw", 0);
    private final Bloco[] blocos = new Bloco[TOTAL_BLOCOS];
    private final Map<Integer, Abertura> tabelaGlobal = new HashMap<>();
    private int proximaAbertura = 1;

    static void validarCaminho(String caminho) {
        if (!caminho.startsWith("/") || (caminho.length() > 1 && caminho.endsWith("/")) || caminho.contains("//")) {
            throw new IllegalArgumentException("Caminho absoluto inválido: " + caminho);
        }
        if (caminho.equals("/")) { return; }
        for (String parte : caminho.substring(1).split("/")) {
            if (!parte.matches("[A-Za-z0-9_.-]+") || parte.equals(".") || parte.equals("..")) {
                throw new IllegalArgumentException("Componente de caminho inválido: " + parte);
            }
        }
    }

    private No localizar(String caminho) {
        validarCaminho(caminho);
        No atual = raiz;
        if (caminho.equals("/")) { return atual; }
        for (String parte : caminho.substring(1).split("/")) {
            exigir(atual.diretorio, "Componente não é diretório: " + parte);
            exigir(atual.permissoes.contains("r"), "Diretório sem permissão de travessia/leitura.");
            atual = atual.filhos.get(parte);
            exigir(atual != null, "Caminho inexistente: " + caminho);
        }
        return atual;
    }

    private No pai(String caminho) {
        validarCaminho(caminho);
        exigir(!caminho.equals("/"), "A raiz não pode ser criada ou removida.");
        int separador = caminho.lastIndexOf('/');
        No pai = localizar(separador == 0 ? "/" : caminho.substring(0, separador));
        exigir(pai.diretorio && pai.permissoes.contains("w"), "Pai não é diretório gravável.");
        return pai;
    }

    void criar(String caminho, boolean diretorio, String permissoes, long clock) {
        exigir(List.of("r", "w", "rw", "-").contains(permissoes), "Permissão inválida.");
        No pai = pai(caminho);
        String nome = caminho.substring(caminho.lastIndexOf('/') + 1);
        exigir(!pai.filhos.containsKey(nome), "Caminho já existe: " + caminho);
        pai.filhos.put(nome, new No(nome, diretorio, permissoes, clock));
        pai.modificacao = clock;
    }

    int abrir(Processo processo, String caminho, String modo) {
        exigir(List.of("r", "w", "rw").contains(modo), "Modo de abertura inválido.");
        No arquivo = localizar(caminho);
        exigir(!arquivo.diretorio, "Não é possível abrir diretório como arquivo.");
        for (char permissao : modo.toCharArray()) {
            exigir(arquivo.permissoes.indexOf(permissao) >= 0, "Acesso incompatível com permissões: " + caminho);
        }
        int descritor = processo.proximoDescritor++;
        int global = proximaAbertura++;
        tabelaGlobal.put(global, new Abertura(arquivo, modo));
        processo.arquivosAbertos.put(descritor, global);
        return descritor;
    }

    private Abertura abertura(Processo processo, int descritor, String permissao) {
        Integer global = processo.arquivosAbertos.get(descritor);
        exigir(global != null, "Descritor fechado/inexistente: " + descritor);
        Abertura abertura = tabelaGlobal.get(global);
        exigir(abertura.modo.contains(permissao), "Descritor sem permissão " + permissao);
        return abertura;
    }

    String ler(Processo processo, int descritor, int quantidade) {
        exigir(quantidade >= 0, "Quantidade de leitura negativa.");
        Abertura abertura = abertura(processo, descritor, "r");
        String conteudo = conteudo(abertura.arquivo);
        int fim = (int) Math.min(conteudo.length(), (long) abertura.posicao + quantidade);
        String trecho = conteudo.substring(abertura.posicao, fim);
        abertura.posicao = fim;
        return trecho;
    }

    void escrever(Processo processo, int descritor, String texto, long clock) {
        Abertura abertura = abertura(processo, descritor, "w");
        String anterior = conteudo(abertura.arquivo);
        int fim = abertura.posicao + texto.length();
        String novo = anterior.substring(0, abertura.posicao) + texto;
        if (fim < anterior.length()) { novo += anterior.substring(fim); }
        List<Integer> antigos = indices(abertura.arquivo);
        List<Integer> disponiveis = new ArrayList<>();
        for (int indice = 0; indice < blocos.length; indice++) {
            if (blocos[indice] == null || antigos.contains(indice)) { disponiveis.add(indice); }
        }
        int necessarios = (novo.length() + TAMANHO_BLOCO - 1) / TAMANHO_BLOCO;
        exigir(necessarios <= disponiveis.size(), "Disco simulado cheio; escrita cancelada integralmente.");
        for (int indice : antigos) { blocos[indice] = null; }
        for (int numero = 0; numero < necessarios; numero++) {
            int inicio = numero * TAMANHO_BLOCO;
            int proximo = numero + 1 < necessarios ? disponiveis.get(numero + 1) : -1;
            blocos[disponiveis.get(numero)] = new Bloco(novo.substring(inicio, Math.min(inicio + TAMANHO_BLOCO, novo.length())), proximo);
        }
        abertura.arquivo.primeiroBloco = necessarios == 0 ? -1 : disponiveis.get(0);
        abertura.arquivo.tamanho = novo.length();
        abertura.arquivo.modificacao = clock;
        abertura.posicao = fim;
    }

    private List<Integer> indices(No arquivo) {
        List<Integer> indices = new ArrayList<>();
        for (int indice = arquivo.primeiroBloco; indice != -1; indice = blocos[indice].proximo()) { indices.add(indice); }
        return indices;
    }
    private String conteudo(No arquivo) {
        StringBuilder texto = new StringBuilder();
        for (int indice : indices(arquivo)) { texto.append(blocos[indice].conteudo()); }
        return texto.toString();
    }

    void fechar(Processo processo, int descritor) {
        Integer global = processo.arquivosAbertos.remove(descritor);
        exigir(global != null, "Descritor fechado/inexistente: " + descritor);
        tabelaGlobal.remove(global);
    }

    void remover(String caminho, long clock) {
        No pai = pai(caminho);
        No arquivo = localizar(caminho);
        exigir(arquivo.filhos.isEmpty(), "Diretório não vazio.");
        for (Abertura abertura : tabelaGlobal.values()) {
            exigir(abertura.arquivo != arquivo, "Arquivo ainda está aberto.");
        }
        for (int indice : indices(arquivo)) { blocos[indice] = null; }
        pai.filhos.remove(arquivo.nome);
        pai.modificacao = clock;
    }

    String listar(String caminho) {
        No diretorio = localizar(caminho);
        exigir(diretorio.diretorio && diretorio.permissoes.contains("r"), "Não é diretório legível.");
        List<String> linhas = new ArrayList<>();
        for (No filho : diretorio.filhos.values()) {
            linhas.add(filho.nome + (filho.diretorio ? "/" : "") + "{tipo=" + (filho.diretorio ? "diretorio" : "arquivo")
                    + ", tamanho=" + filho.tamanho + ", permissoes=" + filho.permissoes + ", criacao=" + filho.criacao
                    + ", modificacao=" + filho.modificacao + ", blocos=" + indices(filho) + "}");
        }
        return linhas.toString();
    }

    private static void exigir(boolean condicao, String mensagem) {
        if (!condicao) { throw new IllegalArgumentException(mensagem); }
    }
}
