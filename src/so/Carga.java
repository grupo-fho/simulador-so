package so;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

final class Carga {
    static List<Processo> ler(Path caminho) throws IOException {
        List<Processo> processos = new ArrayList<>();
        Set<String> identificadores = new HashSet<>();
        Processo processo = null;
        ThreadSimulada thread = null;
        int linha = 0;
        for (String texto : Files.readAllLines(caminho, StandardCharsets.UTF_8)) {
            linha++;
            texto = texto.strip();
            if (texto.isEmpty() || texto.startsWith("#")) { continue; }
            try {
                List<String> palavras = separar(texto);
                String comando = palavras.get(0);
                switch (comando) {
                    case "PROCESSO" -> {
                        exigir(palavras.size() == 5 && processo == null, "Use PROCESSO id chegada prioridade paginas fora de outro processo.");
                        String id = palavras.get(1);
                        exigir(id.matches("[A-Za-z0-9_-]+") && identificadores.add(id), "ID inválido ou duplicado.");
                        processo = new Processo(id, natural(palavras.get(2), false),
                                natural(palavras.get(3), false), natural(palavras.get(4), true));
                        processos.add(processo);
                    }
                    case "THREAD" -> {
                        exigir(palavras.size() == 2 && processo != null && thread == null, "THREAD fora de processo ou aninhada.");
                        String id = palavras.get(1);
                        exigir(id.matches("[A-Za-z0-9_-]+"), "ID de thread inválido.");
                        for (ThreadSimulada existente : processo.threads) {
                            exigir(!existente.id.equals(id), "ID de thread duplicado no processo.");
                        }
                        thread = new ThreadSimulada(id, processo);
                        processo.threads.add(thread);
                    }
                    case "FIM_THREAD" -> {
                        exigir(palavras.size() == 1 && thread != null && !thread.instrucoes.isEmpty(), "Thread ausente ou vazia.");
                        thread = null;
                    }
                    case "FIM_PROCESSO" -> {
                        exigir(palavras.size() == 1 && processo != null && thread == null && !processo.threads.isEmpty(), "Processo incompleto.");
                        processo = null;
                    }
                    default -> {
                        exigir(thread != null, "Instrução fora de thread.");
                        Instrucao instrucao = new Instrucao(comando, List.copyOf(palavras.subList(1, palavras.size())), linha);
                        validar(instrucao, processo);
                        thread.instrucoes.add(instrucao);
                    }
                }
            } catch (IllegalArgumentException erro) {
                throw new IllegalArgumentException(caminho + ":" + linha + ": " + erro.getMessage());
            }
        }
        exigir(processo == null && thread == null && !processos.isEmpty(), "Carga vazia ou sem FIM_THREAD/FIM_PROCESSO.");
        return processos;
    }

    // Aspas preservam espaços; não há escapes nem comentários ao fim da linha.
    static List<String> separar(String texto) {
        List<String> palavras = new ArrayList<>();
        StringBuilder palavra = new StringBuilder();
        boolean aspas = false;
        boolean iniciada = false;
        for (char caractere : texto.toCharArray()) {
            if (caractere == '"') { aspas = !aspas; iniciada = true; }
            else if (Character.isWhitespace(caractere) && !aspas) {
                if (iniciada) { palavras.add(palavra.toString()); palavra.setLength(0); iniciada = false; }
            } else { palavra.append(caractere); iniciada = true; }
        }
        exigir(!aspas, "Aspas não fechadas.");
        if (iniciada) { palavras.add(palavra.toString()); }
        return palavras;
    }

    private static void validar(Instrucao instrucao, Processo processo) {
        int quantidade = switch (instrucao.operacao()) {
            case "CPU", "MEM", "FECHAR", "REMOVER", "LISTAR", "EMPILHAR" -> 1;
            case "IO", "CRIAR", "MKDIR", "ABRIR", "LER", "ESCREVER" -> 2;
            case "DESEMPILHAR" -> 0;
            default -> throw new IllegalArgumentException("Instrução desconhecida: " + instrucao.operacao());
        };
        exigir(instrucao.argumentos().size() == quantidade, "Quantidade de argumentos incorreta para " + instrucao.operacao());
        switch (instrucao.operacao()) {
            case "CPU", "EMPILHAR" -> natural(instrucao.argumento(0), true);
            case "MEM" -> natural(instrucao.argumento(0), false);
            case "IO" -> {
                exigir(Set.of("disco", "terminal").contains(instrucao.argumento(0)), "Dispositivo deve ser disco ou terminal.");
                exigir(Set.of("B", "NB").contains(instrucao.argumento(1)), "IO deve usar B ou NB.");
            }
            case "CRIAR", "MKDIR" -> {
                Arquivos.validarCaminho(instrucao.argumento(0));
                exigir(Set.of("r", "w", "rw", "-").contains(instrucao.argumento(1)), "Permissão deve ser r, w, rw ou -.");
            }
            case "ABRIR" -> {
                Arquivos.validarCaminho(instrucao.argumento(0));
                exigir(Set.of("r", "w", "rw").contains(instrucao.argumento(1)), "Modo deve ser r, w ou rw.");
            }
            case "REMOVER", "LISTAR" -> Arquivos.validarCaminho(instrucao.argumento(0));
            case "LER" -> { natural(instrucao.argumento(0), false); natural(instrucao.argumento(1), false); }
            case "FECHAR", "ESCREVER" -> natural(instrucao.argumento(0), false);
            default -> { }
        }
        exigir(processo.paginas > 0, "Processo sem espaço lógico.");
    }

    private static int natural(String texto, boolean positivo) {
        try {
            int numero = Integer.parseInt(texto);
            exigir(numero >= (positivo ? 1 : 0) && numero <= 1_000_000, "Número fora do intervalo permitido (até 1000000).");
            return numero;
        } catch (NumberFormatException erro) {
            throw new IllegalArgumentException("Inteiro inválido: " + texto);
        }
    }

    private static void exigir(boolean condicao, String mensagem) {
        if (!condicao) { throw new IllegalArgumentException(mensagem); }
    }
}
