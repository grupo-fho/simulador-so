import copy
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from simulador.arquivos import SistemaArquivos
from simulador.carga import carregar_arquivo, carregar_texto, construir_processos
from simulador.configuracao import Configuracao
from simulador.eventos import AgendaEventos, RegistroEventos
from simulador.memoria import GerenciadorMemoria
from simulador.modelo import ErroSimulacao, Estado
from simulador.nucleo import Simulador
from simulador.terminal import executar_experimentos, main


RAIZ = Path(__file__).resolve().parent.parent


def cpu(duracao):
    return {"op": "cpu", "duracao": duracao}


def memoria(endereco):
    return {"op": "memoria", "endereco": endereco}


def es(bloqueante=True, dispositivo="disco"):
    return {"op": "es", "dispositivo": dispositivo, "bloqueante": bloqueante}


def tarefa(identificador, instrucoes, chegada=0, prioridade=0, outras_threads=()):
    return {"id": identificador, "chegada": chegada, "prioridade": prioridade,
            "memoria": 128, "threads": [{"id": f"T{n}", "instrucoes": programa}
                                        for n, programa in enumerate([instrucoes, *outras_threads], 1)]}


def simular(*tarefas, **configuracao):
    simulador = Simulador(construir_processos({"processos": list(tarefas)}), Configuracao(**configuracao))
    simulador.executar()
    return simulador


class TesteEventosEscalonamento(unittest.TestCase):
    def test_agenda_estavel(self):
        agenda = AgendaEventos()
        for tipo, instante in [("B", 2), ("A", 1), ("C", 2)]:
            agenda.agendar(instante, tipo, lambda: None)
        self.assertEqual([agenda.proximo().tipo for _ in range(3)], ["A", "B", "C"])

    def test_fcfs_metricas_conferiveis_a_mao(self):
        sim = simular(tarefa("P1", [cpu(3)]), tarefa("P2", [cpu(2)]), algoritmo="fcfs")
        self.assertEqual(sim.metricas()["tempo_total"], 5)
        self.assertEqual(sim.metricas()["threads"], [
            {"thread": "P1/T1", "retorno": 3, "espera": 0, "resposta": 0, "cpu": 3},
            {"thread": "P2/T1", "retorno": 5, "espera": 3, "resposta": 3, "cpu": 2}])

    def test_rr_quantum_e_contexto_salvo(self):
        sim = simular(tarefa("P1", [cpu(3)]), tarefa("P2", [cpu(2)]), quantum=2)
        despachos = [(r.clock, r.objeto) for r in sim.log.registros if r.tipo == "DESPACHO"]
        self.assertEqual(despachos, [(0, "P1/T1"), (2, "P2/T1"), (4, "P1/T1")])
        self.assertEqual(sim.metricas()["threads"][0]["espera"], 2)
        self.assertEqual(sum(r.tipo == "PREEMPCAO" for r in sim.log.registros), 1)
        self.assertEqual(sim.processos["P1"].threads[0].tcb.registradores["cpu_executada"], 3)

    def test_quantum_acumula_entre_surtos_adjacentes(self):
        sim = simular(tarefa("P1", [cpu(1), cpu(2)]), tarefa("P2", [cpu(1)]), quantum=2)
        self.assertEqual([(r.clock, r.objeto) for r in sim.log.registros if r.tipo == "DESPACHO"],
                         [(0, "P1/T1"), (2, "P2/T1"), (3, "P1/T1")])

    def test_prioridades_e_desempate(self):
        sim = simular(tarefa("P3", [cpu(1)], prioridade=2),
                      tarefa("P2", [cpu(1)], prioridade=0),
                      tarefa("P1", [cpu(1)], prioridade=0), algoritmo="prioridades")
        self.assertEqual([r.objeto for r in sim.log.registros if r.tipo == "DESPACHO"],
                         ["P1/T1", "P2/T1", "P3/T1"])

    def test_prioridades_nao_preemptivas(self):
        sim = simular(tarefa("P1", [cpu(5)], prioridade=5),
                      tarefa("P2", [cpu(1)], chegada=1, prioridade=0), algoritmo="prioridades")
        self.assertEqual(sim.metricas()["threads"][1]["resposta"], 4)

    def test_custo_contexto_separado_da_cpu_util(self):
        sim = simular(tarefa("P1", [cpu(2)]), custo_contexto=3)
        met = sim.metricas()
        self.assertEqual((met["tempo_total"], met["cpu_util"], met["tempo_contexto"]), (5, 2, 3))
        self.assertEqual(met["threads"][0]["resposta"], 3)
        self.assertAlmostEqual(met["utilizacao_cpu"], 0.4)
        self.assertEqual(met["cpu_ociosa"], 0)

    def test_chegada_tardia_conta_ociosidade(self):
        sim = simular(tarefa("P1", [cpu(2)], chegada=4))
        self.assertEqual(sim.metricas()["cpu_ociosa"], 4)
        self.assertEqual(sim.metricas()["threads"][0]["retorno"], 2)

    def test_transicao_invalida_e_reexecucao(self):
        sim = simular(tarefa("P1", [cpu(1)]))
        with self.assertRaises(ErroSimulacao):
            sim._mudar_estado(sim.processos["P1"].threads[0], Estado.PRONTO, "inválida")
        with self.assertRaises(ErroSimulacao):
            sim.executar()


class TesteMemoriaES(unittest.TestCase):
    def test_traducao_e_limite_do_espaco(self):
        processos = construir_processos({"processos": [tarefa("P1", [cpu(1)])]})
        memoria_ = GerenciadorMemoria(16, 2, {"P1": processos[0]})
        self.assertIsNone(memoria_.acessar("P1", 19))
        self.assertEqual(memoria_.carregar("P1", 1), (0, None))
        self.assertEqual(memoria_.acessar("P1", 19), 3)
        with self.assertRaises(ErroSimulacao):
            memoria_.acessar("P1", 128)

    def test_fifo_nao_e_lru(self):
        processos = construir_processos({"processos": [tarefa("P1", [cpu(1)])]})
        memoria_ = GerenciadorMemoria(16, 2, {"P1": processos[0]})
        memoria_.carregar("P1", 0)
        memoria_.carregar("P1", 1)
        memoria_.acessar("P1", 0)
        self.assertEqual(memoria_.carregar("P1", 2), (0, ("P1", 0)))
        self.assertFalse(processos[0].pcb.espaco_enderecamento.tabela_paginas[0].presente)

    def test_falta_bloqueia_e_desbloqueia(self):
        sim = simular(tarefa("P1", [memoria(0), cpu(1), memoria(0), memoria(16), cpu(1)]), numero_molduras=1)
        self.assertEqual(sim.metricas()["faltas_pagina"], 2)
        self.assertEqual(sim.metricas()["acertos_memoria"], 1)
        self.assertEqual(sim.metricas()["tempo_total"], 8)
        self.assertTrue(any(r.tipo == "SUBSTITUICAO_FIFO" for r in sim.log.registros))
        self.assertEqual(sim.memoria.molduras, [None])

    def test_pagina_compartilhada_agrupa_carregamento(self):
        sim = simular(tarefa("P1", [memoria(0), cpu(1)], outras_threads=([memoria(1), cpu(1)],)),
                      numero_molduras=1)
        self.assertEqual(sim.metricas()["faltas_pagina"], 2)
        self.assertEqual(sum(r.tipo == "CARREGAMENTO_PAGINA" for r in sim.log.registros), 1)
        self.assertEqual(sim.metricas()["tempo_total"], 5)

    def test_espacos_independentes_com_uma_moldura(self):
        sim = simular(tarefa("P1", [memoria(0), cpu(1)]), tarefa("P2", [memoria(0), cpu(1)]), numero_molduras=1)
        self.assertEqual(sim.metricas()["faltas_pagina"], 2)
        self.assertEqual(sim.metricas()["tempo_total"], 7)

    def test_es_bloqueante_libera_cpu_para_outra_thread(self):
        sim = simular(tarefa("P1", [cpu(1), es(), cpu(1)], outras_threads=([cpu(2)],)), algoritmo="fcfs")
        self.assertEqual(sim.metricas()["tempo_total"], 6)
        self.assertEqual(sim.metricas()["dispositivos"]["disco"]["tempo_ocupado"], 4)
        self.assertEqual(sim.processos["P1"].threads[1].tcb.finalizacao, 3)
        self.assertEqual(len(sim.processos["P1"].threads[0].tcb.notificacoes), 1)

    def test_es_nao_bloqueante_nao_faz_espera_ativa(self):
        sim = simular(tarefa("P1", [es(False), cpu(2)]))
        self.assertEqual(sim.processos["P1"].pcb.finalizacao, 2)
        self.assertEqual(sim.metricas()["tempo_total"], 4)
        self.assertEqual(sim.metricas()["cpu_util"], 2)
        self.assertEqual(sim.metricas()["trocas_contexto"], 1)
        self.assertFalse(any("-> bloqueado" in r.descricao for r in sim.log.registros))

    def test_filas_de_dispositivo_fcfs_e_independentes(self):
        sim = simular(tarefa("P1", [es(), cpu(1)]), tarefa("P2", [es(), cpu(1)]),
                      tarefa("P3", [es(dispositivo="terminal"), cpu(1)]))
        self.assertEqual([(r.clock, r.objeto) for r in sim.log.registros if r.tipo == "INTERRUPCAO"],
                         [(2, "terminal"), (4, "disco"), (8, "disco")])
        self.assertEqual(sim.metricas()["tempo_total"], 9)


class TesteArquivos(unittest.TestCase):
    def setUp(self):
        self.pcb = construir_processos({"processos": [tarefa("P1", [cpu(1)])]})[0].pcb
        self.outro_pcb = construir_processos({"processos": [tarefa("P2", [cpu(1)])]})[0].pcb
        self.fs = SistemaArquivos(4, 3, RegistroEventos())
        self.fs.criar("/aula", True, "rw", 0)
        self.fs.criar("/aula/notas", False, "rw", 1)

    def test_criar_escrever_ler_fechar_encadeamento(self):
        fd = self.fs.abrir(self.pcb, "/aula/notas", "w", 2)
        self.fs.escrever(self.pcb, fd, "abcdefghij", 3)
        self.assertEqual(self.fs.blocos[0].proximo, 1)
        self.assertEqual(self.fs.blocos[1].proximo, 2)
        self.assertIsNone(self.fs.blocos[2].proximo)
        self.fs.fechar(self.pcb, fd, 4)
        fd = self.fs.abrir(self.pcb, "/aula/notas", "r", 5)
        self.assertEqual(self.fs.ler(self.pcb, fd, 3, 6), b"abc")
        self.assertEqual(self.fs.ler(self.pcb, fd, None, 7), b"defghij")
        self.assertEqual(self.fs.ler(self.pcb, fd, None, 8), b"")
        self.assertEqual(self.fs.localizar("/aula/notas").fcb.modificacao, 3)

    def test_descritores_locais_e_aberturas_independentes(self):
        fd1 = self.fs.abrir(self.pcb, "/aula/notas", "rw", 0)
        fd2 = self.fs.abrir(self.outro_pcb, "/aula/notas", "r", 0)
        self.assertEqual((fd1, fd2), (0, 0))
        self.assertNotEqual(self.pcb.arquivos_abertos[fd1], self.outro_pcb.arquivos_abertos[fd2])
        self.fs.escrever(self.pcb, fd1, "ola", 1)
        self.assertEqual(self.fs.ler(self.outro_pcb, fd2, None, 2), b"ola")
        self.fs.fechar(self.pcb, fd1, 3)
        with self.assertRaises(ErroSimulacao):
            self.fs.ler(self.pcb, fd1, None, 4)

    def test_falta_de_espaco_preserva_dados_e_posicao(self):
        fd = self.fs.abrir(self.pcb, "/aula/notas", "rw", 0)
        self.fs.escrever(self.pcb, fd, "abc", 1)
        with self.assertRaises(ErroSimulacao):
            self.fs.escrever(self.pcb, fd, "0123456789012", 2)
        self.assertEqual(self.fs.conteudo(self.fs.localizar("/aula/notas")), b"abc")
        self.assertEqual(next(iter(self.fs.tabela_global.values())).posicao, 3)

    def test_permissoes_e_modo(self):
        self.fs.criar("/somente_leitura", False, "r", 0)
        with self.assertRaises(ErroSimulacao):
            self.fs.abrir(self.pcb, "/somente_leitura", "w", 0)
        fd = self.fs.abrir(self.pcb, "/aula/notas", "r", 0)
        with self.assertRaises(ErroSimulacao):
            self.fs.escrever(self.pcb, fd, "x", 0)
        with self.assertRaises(ErroSimulacao):
            self.fs.abrir(self.pcb, "/aula", "r", 0)

    def test_remocao_listagem_e_liberacao(self):
        fd = self.fs.abrir(self.pcb, "/aula/notas", "w", 0)
        self.fs.escrever(self.pcb, fd, "abc", 1)
        with self.assertRaises(ErroSimulacao):
            self.fs.remover("/aula/notas", 2)
        with self.assertRaises(ErroSimulacao):
            self.fs.remover("/aula", 2)
        self.fs.fechar(self.pcb, fd, 2)
        self.fs.remover("/aula/notas", 3)
        self.assertEqual(self.fs.listar("/aula", 3), [])
        self.assertEqual(self.fs.blocos, {})
        self.fs.remover("/aula", 4)
        with self.assertRaises(ErroSimulacao):
            self.fs.remover("/aula", 5)

    def test_append_utf8_e_truncamento(self):
        fd = self.fs.abrir(self.pcb, "/aula/notas", "a", 0)
        self.fs.escrever(self.pcb, fd, "á", 1)
        self.fs.escrever(self.pcb, fd, "b", 2)
        self.assertEqual(self.fs.localizar("/aula/notas").fcb.tamanho, 3)
        self.fs.fechar(self.pcb, fd, 3)
        self.fs.abrir(self.pcb, "/aula/notas", "w", 4)
        self.assertEqual(self.fs.blocos, {})

    def test_caminhos_invalidos(self):
        for caminho in ["relativo", "/aula//notas", "/aula/../notas", "/aula/notas/"]:
            with self.subTest(caminho=caminho), self.assertRaises(ErroSimulacao):
                self.fs.localizar(caminho)


class TesteIntegracaoValidacao(unittest.TestCase):
    def test_todas_cargas_nas_tres_politicas(self):
        for caminho in sorted((RAIZ / "cargas").glob("*.json")):
            for algoritmo in ("fcfs", "rr", "prioridades"):
                with self.subTest(carga=caminho.name, algoritmo=algoritmo):
                    sim = Simulador(carregar_arquivo(str(caminho)), Configuracao(algoritmo=algoritmo, custo_contexto=1))
                    met = sim.executar()
                    self.assertTrue(all(p.pcb.estado == Estado.FINALIZADO for p in sim.processos.values()))
                    self.assertFalse(sim.arquivos.tabela_global)
                    self.assertGreaterEqual(met["cpu_ociosa"], 0)
                    self.assertEqual(met["cpu_util"] + met["tempo_contexto"] + met["cpu_ociosa"], met["tempo_total"])
                    self.assertEqual([r.clock for r in sim.log.registros], sorted(r.clock for r in sim.log.registros))
                    self.assertEqual(met["erros_arquivos"], 3 if caminho.stem == "arquivos" else 0)

    def test_determinismo_integral(self):
        caminho = str(RAIZ / "cargas" / "mista.json")
        a = Simulador(carregar_arquivo(caminho), Configuracao(custo_contexto=1))
        b = Simulador(carregar_arquivo(caminho), Configuracao(custo_contexto=1))
        self.assertEqual(a.executar(), b.executar())
        self.assertEqual(a.log.registros, b.log.registros)

    def test_arquivo_finaliza_sem_fechar_explicitamente(self):
        sim = simular(tarefa("P1", [{"op": "criar_arquivo", "caminho": "/x"},
                                    {"op": "abrir", "caminho": "/x", "modo": "rw"}, cpu(1)]))
        self.assertFalse(sim.arquivos.tabela_global)
        self.assertFalse(sim.processos["P1"].pcb.arquivos_abertos)

    def test_entrada_invalida_rejeitada(self):
        dados = {"processos": [tarefa("P1", [cpu(1)])]}
        invalidos = [None, {}, {"processos": []}, {"processos": [dados["processos"][0]] * 2}]
        for campo, valor in [("chegada", -1), ("memoria", 0), ("prioridade", True), ("threads", [])]:
            copia = copy.deepcopy(dados)
            copia["processos"][0][campo] = valor
            invalidos.append(copia)
        for instrucao in [cpu(0), memoria(128), {"op": "invalida"}, {"op": "es", "dispositivo": "rede"},
                          {"op": "ler", "fd": -1}, {"op": "cpu", "duracao": 1, "durcao": 2}]:
            invalidos.append({"processos": [tarefa("P1", [instrucao])]})
        for dados_invalidos in invalidos:
            with self.subTest(dados=dados_invalidos), self.assertRaises(ErroSimulacao):
                construir_processos(dados_invalidos)
        with self.assertRaises(ErroSimulacao):
            carregar_texto("{")

    def test_parametros_invalidos(self):
        for parametro in [{"quantum": 0}, {"custo_contexto": -1}, {"numero_molduras": 0}, {"algoritmo": "x"}]:
            with self.assertRaises(ErroSimulacao):
                Configuracao(**parametro)

    def test_terminal_stdin_json_e_erro(self):
        carga = json.dumps({"processos": [tarefa("P1", [cpu(1)])]})
        with patch("sys.stdin", io.StringIO(carga)), patch("sys.stdout", new_callable=io.StringIO) as saida:
            self.assertEqual(main(["--carga", "-", "--json"]), 0)
            self.assertEqual(json.loads(saida.getvalue())["metricas"]["tempo_total"], 1)
        with patch("sys.stderr", new_callable=io.StringIO) as erro:
            self.assertEqual(main(["--quantum", "0"]), 2)
            self.assertIn("quantum", erro.getvalue())

    def test_nucleo_nao_abre_nem_grava_arquivos_reais(self):
        processos = carregar_arquivo(str(RAIZ / "cargas" / "arquivos.json"))
        with patch("builtins.open", side_effect=AssertionError("acesso real proibido")), \
                patch("io.open", side_effect=AssertionError("acesso real proibido")):
            sim = Simulador(processos, Configuracao())
            self.assertEqual(sim.executar()["erros_arquivos"], 3)

    def test_experimentos_controlam_variaveis(self):
        resultados = executar_experimentos(Configuracao())
        self.assertEqual(len(resultados), 7)
        self.assertEqual(resultados[-2]["metricas"]["faltas_pagina"], 11)
        self.assertEqual(resultados[-1]["metricas"]["faltas_pagina"], 4)


if __name__ == "__main__":
    unittest.main()
