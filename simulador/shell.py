"""Terminal contínuo sobre o sistema de arquivos e os processos do simulador."""

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict
from io import StringIO
import json
import posixpath
import shlex
import sys

from .carga import carregar_arquivo
from .configuracao import Configuracao
from .modelo import ErroSimulacao, EspacoEnderecamento, PCB
from .nucleo import Simulador
from .terminal import PASTA_CARGAS, apresentar_metricas, criar_parser, main
from .texto import TextoSO


RESET = "\033[0m"
CIANO = "\033[1;36m"
VERDE = "\033[1;32m"
VERMELHO = "\033[1;31m"
AMARELO = "\033[1;33m"


def colorir(texto: str, cor: str, ativo: bool) -> str:
    if not ativo or "\033[" in texto:
        return texto
    return f"{cor}{texto}{RESET}"


def ajuda(colorida: bool) -> str:
    comando = lambda texto: colorir(texto, CIANO, colorida)
    return f"""
Comandos de arquivos:

    {comando("ls")} [pasta]    {comando("pwd")}             {comando("cd")} pasta
    {comando("mkdir")} pasta   {comando("rm")} caminho      {comando("create")} arquivo.sotxt
    {comando("edit")} arquivo.sotxt [texto]    {comando("cat")} arquivo.sotxt

Simulação:
    {comando("load")} [cenario|arquivo.json] [opções]
    {comando("step")} [quantidade]             {comando("run")}
    {comando("ps")}            {comando("metricas")}       {comando("log")} [quantidade]
    {comando("config")}        {comando("experimentos")} [opções]

Editor: {colorir(".salvar", AMARELO, colorida)} grava; {colorir(".cancelar", AMARELO, colorida)} descarta.
Nomes .txt viram .sotxt.
Cenários: cpu, es, mista, verificacao, memoria, arquivos.

{colorir("sair", VERMELHO, colorida)}
"""


AJUDA = ajuda(False)


class Shell:
    def __init__(self, simulador: Simulador) -> None:
        self.sim = simulador
        self.fs = simulador.arquivos
        self.pcb = PCB("SHELL", 0, 0, EspacoEnderecamento(256))
        self.pasta = "/"
        self.andamento = simulador.passos()
        self.ativo = True
        self._ultimo_painel = self.painel_processos()
        self._mostrar_processos = False

    def caminho(self, nome: str, texto: bool = False) -> str:
        caminho = posixpath.normpath(posixpath.join(self.pasta, nome))
        if texto:
            base, extensao = posixpath.splitext(caminho)
            if extensao not in {"", ".txt", TextoSO.extensao}:
                raise ErroSimulacao("O editor usa a extensão .sotxt.")
            caminho = base + TextoSO.extensao
        return caminho

    def ler(self, caminho: str) -> str:
        fd = self.fs.abrir(self.pcb, caminho, "r", self.sim.clock)
        try:
            dados = self.fs.ler(self.pcb, fd, None, self.sim.clock)
            return TextoSO.decodificar(dados) if caminho.endswith(TextoSO.extensao) else dados.decode("utf-8")
        finally:
            self.fs.fechar(self.pcb, fd, self.sim.clock)

    def salvar(self, caminho: str, texto: str) -> None:
        fd = self.fs.abrir(self.pcb, caminho, "rw", self.sim.clock)
        try:
            self.fs.escrever(self.pcb, fd, TextoSO.codificar(texto), self.sim.clock, substituir=True)
        finally:
            self.fs.fechar(self.pcb, fd, self.sim.clock)

    def passo(self) -> None:
        if self.andamento is not None:
            try:
                next(self.andamento)
            except StopIteration:
                self.andamento = None

    def mostrar(self, mensagem: str) -> None:
        colorida = sys.stdout.isatty()
        if colorida:
            print("\033[2J\033[H", end="")
        cabecalho = f"SO / TERMINAL    {self.pasta}    |    disco: {len(self.fs.blocos)}/{self.fs.numero_blocos} blocos"
        print(colorir(cabecalho, CIANO, colorida))
        print(colorir(mensagem, VERDE, colorida))
        painel = self.painel_processos()
        if self._mostrar_processos or painel != self._ultimo_painel:
            print(painel)
        self._ultimo_painel, self._mostrar_processos = painel, False

    def painel_processos(self) -> str:
        linhas = [f"\nPROCESSOS / clock {self.sim.clock} / {self.sim.configuracao.algoritmo}",
                  f"{'PID':<10} {'ESTADO':<12} {'THREAD':<10} {'ESTADO':<12} {'PC':>4} {'CPU':>5}"]
        for processo in self.sim.processos.values():
            for thread in processo.threads:
                tcb = thread.tcb
                linhas.append(f"{processo.pcb.identificador:<10} {processo.pcb.estado.value:<12} "
                              f"{tcb.identificador:<10} {tcb.estado.value:<12} {tcb.contador_programa:>4} {tcb.tempo_cpu:>5}")
        return "\n".join(linhas)

    def comando(self, linha: str) -> str:
        partes = shlex.split(linha)
        if not partes:
            return ""
        comando, *args = partes
        limites = {"help": (0, 0), "ls": (0, 1), "pwd": (0, 0), "cd": (1, 1),
                   "mkdir": (1, 1), "create": (1, 1), "edit": (1, sys.maxsize),
                   "cat": (1, 1), "rm": (1, 1), "load": (0, sys.maxsize),
                   "step": (0, 1), "run": (0, 0), "ps": (0, 0), "metricas": (0, 0),
                   "log": (0, 1), "config": (0, 0), "experimentos": (0, sys.maxsize), "sair": (0, 0)}
        if comando not in limites or not limites[comando][0] <= len(args) <= limites[comando][1]:
            raise ErroSimulacao("Comando ou argumentos inválidos. Digite help.")
        if comando == "sair":
            self.ativo = False
            return "Sessão encerrada; disco virtual descartado."
        if comando == "help":
            return ajuda(sys.stdout.isatty())
        if comando == "pwd":
            return self.pasta
        if comando == "ls":
            entradas = self.fs.listar(self.caminho(args[0] if args else "."), self.sim.clock)
            return "\n".join(f"{e['tipo']:<10} {e['tamanho']:>6} B  {e['nome']}" for e in entradas) or "Pasta vazia."
        if comando == "cd":
            caminho = self.caminho(args[0])
            self.fs.listar(caminho, self.sim.clock)
            self.pasta = caminho
            return caminho
        if comando in {"mkdir", "create"}:
            caminho = self.caminho(args[0], texto=comando == "create")
            self.fs.criar(caminho, comando == "mkdir", "rw", self.sim.clock)
            return f"Criado: {caminho}"
        if comando in {"cat", "rm"}:
            caminho = self.caminho(args[0])
            try:
                self.fs.localizar(caminho)
            except ErroSimulacao:
                caminho = self.caminho(args[0], texto=True)
            if comando == "cat":
                return self.ler(caminho)
            if caminho == self.pasta or self.pasta.startswith(caminho + "/"):
                raise ErroSimulacao("Saia deste diretório antes de removê-lo.")
            self.fs.remover(caminho, self.sim.clock)
            return f"Removido: {caminho}"
        if comando == "edit":
            caminho = self.caminho(args[0], texto=True)
            atual = self.ler(caminho)
            texto = " ".join(args[1:])
            if len(args) == 1:
                print(f"EDITOR / {caminho}\nAtual:\n{atual}\nDigite o novo texto; .salvar grava, .cancelar descarta.")
                linhas = []
                while True:
                    linha = input("| ")
                    if linha == ".cancelar":
                        return "Edição cancelada."
                    if linha == ".salvar":
                        break
                    linhas.append(linha)
                texto = "\n".join(linhas)
            self.salvar(caminho, texto)
            return f"Salvo no disco virtual: {caminho}"
        if comando == "load":
            if args and not args[0].startswith("--"):
                origem = args.pop(0)
                args = ["--cenario" if (PASTA_CARGAS / f"{origem}.json").is_file() else "--carga", origem, *args]
            parser = criar_parser()
            parser.set_defaults(**asdict(self.sim.configuracao))
            with redirect_stdout(StringIO()) as saida, redirect_stderr(saida):
                try:
                    opcoes = parser.parse_args(args)
                except SystemExit:
                    return saida.getvalue()
            config = Configuracao(**{n: getattr(opcoes, n) for n in Configuracao.__dataclass_fields__})
            if (config.tamanho_bloco, config.numero_blocos) != (self.fs.tamanho_bloco, self.fs.numero_blocos):
                raise ErroSimulacao("Configure o tamanho do disco ao iniciar: python main.py --interativo --numero-blocos N.")
            carga = opcoes.carga or str(PASTA_CARGAS / f"{opcoes.cenario}.json")
            simulador = Simulador(carregar_arquivo(carga), config)
            for processo in self.sim.processos.values():
                self.fs.fechar_todos(processo.pcb, self.sim.clock)
            simulador.arquivos = self.fs
            self.fs.log = simulador.log
            self.sim, self.andamento = simulador, simulador.passos()
            return "Carga pronta. Use step ou run. O disco virtual foi mantido."
        if comando in {"step", "run"}:
            quantidade = int(args[0]) if args else 1
            if quantidade < 1:
                raise ErroSimulacao("A quantidade de passos deve ser positiva.")
            if comando == "run":
                while self.andamento is not None:
                    self.passo()
            else:
                for _ in range(quantidade):
                    self.passo()
            return "Simulação concluída." if self.andamento is None else "Pausado. Use step ou run."
        if comando == "ps":
            self._mostrar_processos = True
            return "Estados atuais dos processos e threads abaixo."
        if comando == "config":
            return json.dumps(asdict(self.sim.configuracao), ensure_ascii=False)
        if comando == "log":
            quantidade = int(args[0]) if args else 10
            if quantidade < 1:
                raise ErroSimulacao("A quantidade de eventos deve ser positiva.")
            return "\n".join(map(str, self.sim.log.registros[-quantidade:])) or "Nenhum evento."
        with redirect_stdout(StringIO()) as saida, redirect_stderr(saida):
            if comando == "experimentos":
                try:
                    main(["--experimentos", *args])
                except SystemExit:
                    pass
            elif comando == "metricas":
                if self.andamento is not None:
                    raise ErroSimulacao("Conclua a simulação com run para consultar métricas finais.")
                apresentar_metricas(self.sim.metricas())
        return saida.getvalue()

    def executar(self) -> int:
        mensagem = ajuda(sys.stdout.isatty())
        while self.ativo:
            self.mostrar(mensagem)
            try:
                prompt = colorir(f"so:{self.pasta}> ", AMARELO, sys.stdout.isatty())
                mensagem = self.comando(input(prompt))
            except EOFError:
                break
            except KeyboardInterrupt:
                mensagem = colorir("Comando cancelado. Digite sair para encerrar.",
                                   AMARELO, sys.stdout.isatty())
            except (ValueError, OSError) as erro:
                mensagem = colorir(f"Erro: {erro}", VERMELHO, sys.stdout.isatty())
        print("Sessão encerrada; disco virtual descartado.")
        return 0
