import io
import unittest
from unittest.mock import patch

from simulador.carga import carregar_arquivo
from simulador.configuracao import Configuracao
from simulador.modelo import ErroSimulacao, Estado
from simulador.nucleo import Simulador
from simulador.shell import Shell
from simulador.terminal import PASTA_CARGAS, main
from simulador.texto import TextoSO


def terminal(**config):
    return Shell(Simulador(carregar_arquivo(str(PASTA_CARGAS / "mista.json")), Configuracao(**config)))


class TesteShell(unittest.TestCase):
    def test_sessao_editor_e_navegacao_sem_arquivos_hospedeiros(self):
        shell = terminal()
        comandos = ["mkdir docs", "cd docs", "create a.txt", "edit a.txt",
                    "Olá", "", "segunda linha", ".salvar", "cat a.txt", "cd ..", "ls", "sair"]
        with patch("builtins.input", side_effect=comandos), patch("sys.stdout", new_callable=io.StringIO) as saida, \
                patch("builtins.open", side_effect=AssertionError("Arquivo hospedeiro proibido")), \
                patch("io.open", side_effect=AssertionError("Arquivo hospedeiro proibido")):
            self.assertEqual(shell.executar(), 0)
        self.assertEqual(shell.ler("/docs/a.sotxt"), "Olá\n\nsegunda linha")
        self.assertEqual(shell.pasta, "/")
        self.assertNotIn("PROCESSOS / clock", saida.getvalue())
        self.assertIn("Salvo no disco virtual", saida.getvalue())
        self.assertFalse(shell.fs.tabela_global)
        self.assertFalse(terminal().fs.raiz.filhos)

    def test_formato_proprio_e_edicao_curta_ou_cancelada(self):
        shell = terminal()
        shell.comando("create a")
        shell.comando('edit a "um texto comprido"')
        shell.comando("edit a á")
        arquivo = shell.fs.localizar("/a.sotxt")
        self.assertEqual(shell.fs.conteudo(arquivo), b"SOTXT/1\n2\n\xc3\xa1")
        self.assertEqual(shell.comando("cat a.txt"), "á")
        with patch("builtins.input", side_effect=["outra edição", ".cancelar"]), \
                patch("sys.stdout", new_callable=io.StringIO):
            shell.comando("edit a")
        self.assertEqual(shell.ler("/a.sotxt"), "á")
        for dados in (b"texto comum", b"SOTXT/1\n9\nabc", b"SOTXT/2\n0\n", b"\xff"):
            with self.subTest(dados=dados), self.assertRaises(ErroSimulacao):
                TextoSO.decodificar(dados)

    def test_disco_cheio_preserva_texto_e_fecha_descritores(self):
        shell = terminal(tamanho_bloco=16, numero_blocos=2)
        shell.comando("create a")
        shell.comando("edit a original")
        with self.assertRaisesRegex(ErroSimulacao, "Disco virtual cheio"):
            shell.salvar("/a.sotxt", "x" * 100)
        self.assertEqual(shell.ler("/a.sotxt"), "original")
        self.assertFalse(shell.fs.tabela_global)

    def test_controles_e_disco_compartilhado_com_processos(self):
        shell = terminal()
        shell.comando("create guardado")
        shell.comando("edit guardado continua aqui")
        shell.comando("step 2")
        self.assertTrue(any(p.pcb.estado == Estado.EXECUTANDO for p in shell.sim.processos.values()))
        clock = shell.sim.clock
        shell.comando("ls")
        self.assertEqual(shell.sim.clock, clock)
        shell.comando("run")
        self.assertEqual(shell.sim.metricas()["tempo_total"], 27)
        self.assertEqual(shell.sim.metricas()["cpu_util"], 22)
        self.assertIn("MÉTRICAS", shell.comando("metricas"))
        shell.comando("load arquivos --algoritmo fcfs")
        self.assertIs(shell.sim.arquivos, shell.fs)
        self.assertEqual(shell.ler("/guardado.sotxt"), "continua aqui")
        shell.comando("run")
        self.assertTrue(any(r.tipo == "LISTAGEM" and "guardado.sotxt" in r.descricao
                            for r in shell.sim.log.registros))
        self.assertEqual(shell.ler("/guardado.sotxt"), "continua aqui")
        self.assertNotIn("aula", shell.fs.raiz.filhos)
        self.assertFalse(shell.fs.tabela_global)

    def test_erro_de_comando_ou_editor_nao_encerra_sessao(self):
        shell = terminal()
        comandos = ["comando-inexistente", "create", "create a", "cd a.sotxt", "step 0",
                    "edit a", KeyboardInterrupt(), "pwd", "load --quantum zero",
                    "experimentos --invalido", "sair"]
        with patch("builtins.input", side_effect=comandos), patch("sys.stdout", new_callable=io.StringIO) as saida:
            self.assertEqual(shell.executar(), 0)
        self.assertIn("Erro:", saida.getvalue())
        self.assertIn("Comando cancelado", saida.getvalue())
        self.assertEqual(shell.ler("/a.sotxt"), "")

    def test_entrada_padrao_abre_terminal_e_eof_encerra(self):
        with patch("builtins.input", side_effect=EOFError), patch("sys.stdout", new_callable=io.StringIO) as saida:
            self.assertEqual(main([]), 0)
        self.assertIn("SO / TERMINAL", saida.getvalue())


if __name__ == "__main__":
    unittest.main()
