package so;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.concurrent.TimeUnit;

/** Testa o contrato do lançador; não substitui uma partida com o motor real. */
public final class TestesDoom {
    private TestesDoom() { }
    public static void main(String[] argumentos) throws Exception {
        Path pasta = Files.createTempDirectory("doom teste com espacos ");
        int verificacoes = 0;
        try {
            Path wad = pasta.resolve("jogo com espacos.wad");
            try { Doom.validarWad(wad); throw new AssertionError("Arquivo ausente aceito."); }
            catch (IOException esperado) { verificacoes++; }
            Files.writeString(wad, "IWAD");
            try { Doom.validarWad(wad); throw new AssertionError("Arquivo truncado aceito."); }
            catch (IOException esperado) { verificacoes++; }
            ByteBuffer bytes = ByteBuffer.allocate(28).order(ByteOrder.LITTLE_ENDIAN);
            bytes.put(new byte[]{'P', 'W', 'A', 'D'}).putInt(1).putInt(12);
            Files.write(wad, bytes.array());
            try { Doom.validarWad(wad); throw new AssertionError("PWAD aceito."); }
            catch (IOException esperado) { verificacoes++; }
            bytes.put(0, (byte) 'I');
            bytes.putInt(8, Integer.MAX_VALUE);
            Files.write(wad, bytes.array());
            try { Doom.validarWad(wad); throw new AssertionError("Diretório fora do arquivo aceito."); }
            catch (IOException esperado) { verificacoes++; }
            bytes.putInt(8, 12);
            Files.write(wad, bytes.array());
            Doom.validarWad(wad);
            verificacoes++;
            Path mod = pasta.resolve("mapas com espacos.wad");
            bytes.put(0, (byte) 'P');
            Files.write(mod, bytes.array());
            Doom.validarMod(mod);
            verificacoes++;
            try { Doom.validarMod(wad); throw new AssertionError("IWAD aceito como mod."); }
            catch (IOException esperado) { verificacoes++; }
            try { Doom.validarMod(pasta.resolve("ausente.wad")); throw new AssertionError("Mod ausente aceito."); }
            catch (IOException esperado) { verificacoes++; }
            Path motor = pasta.resolve("motor com espacos.exe");
            var comando = Doom.comando(motor, wad, mod, pasta);
            if (!comando.get(comando.indexOf("-iwad") + 1).equals(wad.toString())
                    || !comando.get(comando.indexOf("-file") + 1).equals(mod.toString())
                    || Doom.comando(motor, wad, null, pasta).contains("-file")
                    || !comando.contains("-fullscreen") || comando.contains("-window")
                    || comando.contains("-width") || comando.contains("-height")) {
                throw new AssertionError("Argumentos IWAD/PWAD incorretos.");
            }
            verificacoes++;
            Doom doom = new Doom();
            try { doom.iniciar(pasta.resolve("ausente"), wad, pasta); throw new AssertionError("Motor ausente aceito."); }
            catch (IOException esperado) { verificacoes++; }
            // Um processo auxiliar controlado confere argumentos e captura de erros no Linux.
            if (Files.isExecutable(Path.of("/bin/sh"))) {
                Path auxiliar = pasta.resolve("motor auxiliar");
                Files.writeString(auxiliar, "#!/bin/sh\nprintf '%s\\n' \"$@\"\nprintf 'diagnostico stderr\\n' >&2\nexit 7\n");
                if (!auxiliar.toFile().setExecutable(true)) { throw new IOException("Sem permissão para testar processo auxiliar."); }
                Process processo = doom.iniciar(auxiliar, wad, pasta.resolve("dados"));
                if (!processo.waitFor(5, TimeUnit.SECONDS)) {
                    processo.destroyForcibly();
                    throw new AssertionError("Processo auxiliar não encerrou.");
                }
                String log = Files.readString(doom.log());
                if (processo.exitValue() != 7 || doom.executando() || !log.contains("-iwad\n" + wad + "\n")
                        || !log.contains("diagnostico stderr") || !log.contains("-fullscreen\n")) {
                    throw new AssertionError("Lançador não preservou argumentos, saída ou código de término.");
                }
                verificacoes++;
            }
            System.out.println("OK: " + verificacoes + " verificações do lançador DOOM; motor real não incluído neste teste.");
        } finally {
            try (var arquivos = Files.walk(pasta)) {
                for (Path arquivo : arquivos.sorted(Comparator.reverseOrder()).toList()) { Files.delete(arquivo); }
            }
        }
    }
}
