package so;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.ArrayList;

/** Inicia o motor real no SO hospedeiro. Não faz parte do clock lógico. */
final class Doom {
    private Process processo;
    private Path log;

    static void validarWad(Path wad) throws IOException {
        validarArquivoWad(wad, "IWAD");
    }

    static void validarMod(Path wad) throws IOException {
        validarArquivoWad(wad, "PWAD");
    }

    private static void validarArquivoWad(Path wad, String tipo) throws IOException {
        if (!Files.isRegularFile(wad)) { throw new IOException("Arquivo WAD não encontrado: " + wad); }
        try (FileChannel arquivo = FileChannel.open(wad)) {
            ByteBuffer cabecalho = ByteBuffer.allocate(12).order(ByteOrder.LITTLE_ENDIAN);
            while (cabecalho.hasRemaining()) {
                if (arquivo.read(cabecalho) < 0) { throw new IOException("WAD incompleto: cabeçalho ausente."); }
            }
            cabecalho.flip();
            byte[] assinatura = new byte[4];
            cabecalho.get(assinatura);
            if (!tipo.equals(new String(assinatura, StandardCharsets.US_ASCII))) {
                if (tipo.equals("PWAD")) { throw new IOException("Selecione um pacote de mapas PWAD no campo opcional."); }
                throw new IOException("Escolha um IWAD base (DOOM.WAD, DOOM1.WAD ou DOOM2.WAD), não um mod PWAD.");
            }
            int entradas = cabecalho.getInt();
            int diretorio = cabecalho.getInt();
            if (entradas <= 0 || diretorio < 12 || diretorio + entradas * 16L > arquivo.size()) {
                throw new IOException("Diretório do WAD inválido ou arquivo incompleto.");
            }
        }
    }

    synchronized Process iniciar(Path motor, Path wad, Path dados) throws IOException {
        return iniciar(motor, wad, null, dados);
    }

    synchronized Process iniciar(Path motor, Path wad, Path mod, Path dados) throws IOException {
        if (executando()) { throw new IOException("O DOOM já está em execução."); }
        motor = motor.toAbsolutePath();
        wad = wad.toAbsolutePath();
        if (!Files.isRegularFile(motor)) { throw new IOException("Selecione o executável do Chocolate Doom."); }
        validarWad(wad);
        if (mod != null) { validarMod(mod); }
        Files.createDirectories(dados);
        log = Files.createTempFile(dados, "doom-", ".log");
        processo = new ProcessBuilder(comando(motor, wad, mod, dados)).directory(motor.getParent().toFile())
                .redirectErrorStream(true).redirectOutput(log.toFile()).start();
        return processo;
    }

    static List<String> comando(Path motor, Path wad, Path mod, Path dados) {
        List<String> comando = new ArrayList<>(List.of(motor.toString(), "-iwad", wad.toString(), "-fullscreen",
                "-savedir", dados.toAbsolutePath().toString(),
                "-config", dados.resolve("default.cfg").toAbsolutePath().toString(),
                "-extraconfig", dados.resolve("chocolate-doom.cfg").toAbsolutePath().toString()));
        if (mod != null) { comando.addAll(List.of("-file", mod.toAbsolutePath().toString())); }
        return List.copyOf(comando);
    }

    synchronized boolean executando() { return processo != null && processo.isAlive(); }
    Path log() { return log; }
}
