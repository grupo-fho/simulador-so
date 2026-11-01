"""Coordena eventos discretos, CPU e recursos. Não realiza entrada/saída real."""

from collections import deque
from dataclasses import asdict
from itertools import count

from .arquivos import SistemaArquivos
from .configuracao import Configuracao
from .entrada_saida import Dispositivo, Requisicao
from .escalonamento import Escalonador
from .eventos import AgendaEventos, RegistroEventos
from .memoria import GerenciadorMemoria
from .modelo import ErroSimulacao, Estado, Processo, Thread


class Simulador:
    TRANSICOES = {
        Estado.NOVO: {Estado.PRONTO},
        Estado.PRONTO: {Estado.EXECUTANDO},
        Estado.EXECUTANDO: {Estado.PRONTO, Estado.BLOQUEADO, Estado.FINALIZADO},
        Estado.BLOQUEADO: {Estado.PRONTO},
        Estado.FINALIZADO: set(),
    }

    def __init__(self, processos: list[Processo], configuracao: Configuracao) -> None:
        self.configuracao = configuracao
        self.processos = {p.pcb.identificador: p for p in processos}
        self.clock = 0
        self.agenda = AgendaEventos()
        self.log = RegistroEventos()
        self.escalonador = Escalonador(configuracao.algoritmo,
                                      {p.pcb.identificador: p.pcb.prioridade for p in processos})
        self.memoria = GerenciadorMemoria(configuracao.tamanho_pagina,
                                         configuracao.numero_molduras, self.processos)
        self.arquivos = SistemaArquivos(configuracao.tamanho_bloco,
                                        configuracao.numero_blocos, self.log)
        self.dispositivos = {
            "disco": Dispositivo("disco", "bloco", configuracao.tempo_disco, self.agenda, self.log),
            "terminal": Dispositivo("terminal", "caractere", configuracao.tempo_terminal, self.agenda, self.log),
        }
        self.thread_atual: Thread | None = None
        self.tempo_cpu = 0
        self.trocas_contexto = 0
        self.tempo_contexto = 0
        self._ids_requisicoes = count(1)
        self._faltas_pendentes: dict[tuple[str, int], list[tuple[Thread, int]]] = {}
        self._fila_paginador: deque[tuple[str, int]] = deque()
        self._paginador_ocupado = False
        self._executado = False

    def _registrar(self, tipo: str, objeto: str, descricao: str) -> None:
        self.log.registrar(self.clock, tipo, objeto, descricao)

    def _atualizar_processo(self, processo: Processo, causa: str) -> None:
        estados = {t.tcb.estado for t in processo.threads}
        if estados == {Estado.FINALIZADO}:
            novo = Estado.FINALIZADO
        elif Estado.EXECUTANDO in estados:
            novo = Estado.EXECUTANDO
        elif Estado.PRONTO in estados:
            novo = Estado.PRONTO
        elif Estado.BLOQUEADO in estados:
            novo = Estado.BLOQUEADO
        else:
            novo = Estado.NOVO
        if novo != processo.pcb.estado:
            anterior = processo.pcb.estado
            processo.pcb.estado = novo
            self._registrar("ESTADO_PROCESSO", processo.pcb.identificador,
                            f"{anterior.value} -> {novo.value}; causa={causa}")
            if novo == Estado.FINALIZADO:
                processo.pcb.finalizacao = self.clock
                self.arquivos.fechar_todos(processo.pcb, self.clock)
                self.memoria.liberar(processo.pcb.identificador)
                self._registrar("LIBERACAO_RECURSOS", processo.pcb.identificador,
                                "Molduras e descritores liberados.")

    def _mudar_estado(self, thread: Thread, novo: Estado, causa: str) -> None:
        tcb = thread.tcb
        if novo not in self.TRANSICOES[tcb.estado]:
            raise ErroSimulacao(f"Transição inválida: {tcb.estado.value} -> {novo.value} em {thread.chave}.")
        anterior = tcb.estado
        tcb.estado = novo
        self._registrar("ESTADO_THREAD", thread.chave,
                        f"{anterior.value} -> {novo.value}; causa={causa}")
        if novo == Estado.PRONTO:
            tcb.entrada_prontos = self.clock
            self.escalonador.adicionar(thread)
            self._registrar("FILA_PRONTOS", thread.chave, causa)
        self._atualizar_processo(self.processos[tcb.processo_id], causa)

    def executar(self) -> dict:
        if self._executado:
            raise ErroSimulacao("Cada instância do simulador pode ser executada somente uma vez.")
        self._executado = True
        self._registrar("CONFIGURACAO", "sistema", repr(asdict(self.configuracao)))
        # Ordem de chegada, ID do processo, ID da thread: admissão determinística.
        for processo in sorted(self.processos.values(), key=lambda p: (p.pcb.chegada, p.pcb.identificador)):
            self.agenda.agendar(processo.pcb.chegada, "CHEGADA",
                                lambda p=processo: self._admitir(p))
        while self.agenda or self.escalonador.fila_prontos or self.thread_atual:
            if self.agenda and (self.thread_atual is not None or not self.escalonador.fila_prontos):
                self.clock = self.agenda.proximo_instante
            # Todos os eventos do instante são processados antes de novo despacho.
            while self.agenda and self.agenda.proximo_instante == self.clock:
                self.agenda.proximo().acao()
            if self.thread_atual is None and self.escalonador.fila_prontos:
                self._despachar()
            elif self.thread_atual is not None and not self.agenda:
                raise RuntimeError("CPU ocupada sem evento de conclusão.")
        if any(p.pcb.estado != Estado.FINALIZADO for p in self.processos.values()):
            raise RuntimeError("Simulação sem eventos, mas existem processos não finalizados.")
        self._registrar("FIM_SIMULACAO", "sistema", "Todos os processos e solicitações foram concluídos.")
        return self.metricas()

    def _admitir(self, processo: Processo) -> None:
        self._registrar("CHEGADA", processo.pcb.identificador, "Processo admitido no clock lógico.")
        for thread in sorted(processo.threads, key=lambda t: t.tcb.identificador):
            self._mudar_estado(thread, Estado.PRONTO, "admissão")

    def _despachar(self) -> None:
        thread = self.escalonador.selecionar()
        self.thread_atual = thread
        thread.tcb.tempo_espera += self.clock - thread.tcb.entrada_prontos
        thread.tcb.quantum_restante = self.configuracao.quantum
        self._mudar_estado(thread, Estado.EXECUTANDO, "despacho")
        self.trocas_contexto += 1
        self._registrar("DESPACHO", thread.chave, "TCB selecionado; contexto será restaurado.")
        self._registrar("INICIO_CONTEXTO", thread.chave, f"custo={self.configuracao.custo_contexto}")
        self.agenda.agendar(self.clock + self.configuracao.custo_contexto,
                            "FIM_CONTEXTO", self._concluir_contexto)

    def _concluir_contexto(self) -> None:
        self.tempo_contexto += self.configuracao.custo_contexto
        thread = self.thread_atual
        thread.tcb.pilha_logica.append("execucao")
        self._registrar("FIM_CONTEXTO", thread.chave,
                        f"pc={thread.tcb.contador_programa}; registradores={thread.tcb.registradores!r}")
        self._executar_instrucoes()

    def _avancar_programa(self, thread: Thread) -> None:
        thread.tcb.contador_programa += 1
        pcb = self.processos[thread.tcb.processo_id].pcb
        pcb.contador_programa = thread.tcb.contador_programa
        pcb.registradores = thread.tcb.registradores.copy()

    def _liberar_cpu(self, thread: Thread, estado: Estado, causa: str) -> None:
        if thread.tcb.pilha_logica:
            thread.tcb.pilha_logica.pop()
        self._registrar("SALVAR_CONTEXTO", thread.chave,
                        f"pc={thread.tcb.contador_programa}; registradores={thread.tcb.registradores!r}")
        self.thread_atual = None
        self._mudar_estado(thread, estado, causa)

    def _executar_instrucoes(self) -> None:
        thread = self.thread_atual
        while self.thread_atual is thread:
            if thread.tcb.contador_programa == len(thread.instrucoes):
                thread.tcb.finalizacao = self.clock
                self._registrar("FINALIZACAO", thread.chave, "Programa concluído.")
                self._liberar_cpu(thread, Estado.FINALIZADO, "fim do programa")
                return
            instrucao = thread.instrucoes[thread.tcb.contador_programa]
            operacao = instrucao["op"]
            if operacao == "cpu":
                self._iniciar_cpu(thread, instrucao["duracao"])
                return
            # Instruções de controle têm duração zero; CPU explícita consome tempo.
            if operacao == "memoria":
                bloqueou = self._acessar_memoria(thread, instrucao["endereco"])
                self._avancar_programa(thread)
                if bloqueou:
                    self._liberar_cpu(thread, Estado.BLOQUEADO, "falta de página")
                    return
            elif operacao == "es":
                self._avancar_programa(thread)
                bloqueante = instrucao.get("bloqueante", True)
                self._solicitar_es(thread, instrucao, bloqueante)
                if bloqueante:
                    self._liberar_cpu(thread, Estado.BLOQUEADO, "solicitação de E/S")
                    return
            else:
                self._executar_arquivo(thread, instrucao)
                self._avancar_programa(thread)

    def _iniciar_cpu(self, thread: Thread, duracao: int) -> None:
        tcb = thread.tcb
        if tcb.cpu_restante == 0:
            tcb.cpu_restante = duracao
        if self.configuracao.algoritmo == "rr" and tcb.quantum_restante == 0:
            self._registrar("PREEMPCAO", thread.chave, "Quantum esgotado.")
            self._liberar_cpu(thread, Estado.PRONTO, "fim de quantum")
            return
        intervalo = tcb.cpu_restante
        if self.configuracao.algoritmo == "rr":
            intervalo = min(intervalo, tcb.quantum_restante)
        if tcb.primeira_cpu is None:
            tcb.primeira_cpu = self.clock
        self._registrar("EXECUCAO_CPU", thread.chave, f"intervalo=[{self.clock}, {self.clock + intervalo})")
        self.agenda.agendar(self.clock + intervalo, "FIM_CPU",
                            lambda: self._concluir_cpu(thread, intervalo))

    def _concluir_cpu(self, thread: Thread, intervalo: int) -> None:
        tcb = thread.tcb
        self.tempo_cpu += intervalo
        tcb.tempo_cpu += intervalo
        tcb.cpu_restante -= intervalo
        tcb.quantum_restante -= intervalo
        tcb.registradores["cpu_executada"] = tcb.tempo_cpu
        if tcb.cpu_restante == 0:
            self._avancar_programa(thread)
        if tcb.cpu_restante > 0 and self.configuracao.algoritmo == "rr" and tcb.quantum_restante == 0:
            self._registrar("PREEMPCAO", thread.chave, "Quantum esgotado; surto ainda incompleto.")
            self._liberar_cpu(thread, Estado.PRONTO, "fim de quantum")
        else:
            self._executar_instrucoes()

    def _solicitar_es(self, thread: Thread, instrucao: dict, bloqueante: bool) -> None:
        dispositivo = self.dispositivos[instrucao["dispositivo"]]
        identificador = next(self._ids_requisicoes)

        def concluir() -> None:
            mensagem = f"requisição {identificador} concluída em {dispositivo.nome}"
            thread.tcb.notificacoes.append(mensagem)
            thread.tcb.registradores[f"es_{identificador}"] = "concluida"
            self._registrar("NOTIFICACAO_ES", thread.chave, mensagem)
            if bloqueante:
                self._mudar_estado(thread, Estado.PRONTO, "interrupção de E/S")

        dispositivo.solicitar(Requisicao(identificador, thread, bloqueante,
                                        instrucao.get("duracao", dispositivo.tempo_servico), concluir), self.clock)

    def _acessar_memoria(self, thread: Thread, endereco: int) -> bool:
        processo_id = thread.tcb.processo_id
        fisico = self.memoria.acessar(processo_id, endereco)
        if fisico is not None:
            thread.tcb.registradores["endereco_fisico"] = fisico
            self._registrar("ACERTO_PAGINA", thread.chave, f"lógico={endereco}; físico={fisico}")
            return False
        pagina, _ = self.memoria.decompor_endereco(processo_id, endereco)
        chave = (processo_id, pagina)
        self._registrar("FALTA_PAGINA", thread.chave, f"página={pagina}; lógico={endereco}")
        if chave not in self._faltas_pendentes:
            self._faltas_pendentes[chave] = []
            self._fila_paginador.append(chave)
        self._faltas_pendentes[chave].append((thread, endereco))
        self._iniciar_paginador()
        return True

    def _iniciar_paginador(self) -> None:
        if self._paginador_ocupado or not self._fila_paginador:
            return
        self._paginador_ocupado = True
        chave = self._fila_paginador.popleft()
        self._registrar("INICIO_PAGINACAO", chave[0], f"página={chave[1]}")
        self.agenda.agendar(self.clock + self.configuracao.tempo_falta_pagina,
                            "CARREGAMENTO_PAGINA", lambda: self._concluir_paginacao(chave))

    def _concluir_paginacao(self, chave: tuple[str, int]) -> None:
        moldura, vitima = self.memoria.carregar(*chave)
        if vitima is not None:
            self._registrar("SUBSTITUICAO_FIFO", chave[0],
                            f"vítima={vitima}; moldura={moldura}")
        self._registrar("CARREGAMENTO_PAGINA", chave[0], f"página={chave[1]}; moldura={moldura}")
        # A referência pendente se completa aqui, mesmo que a página seja removida
        # antes do próximo despacho. Não contamos uma segunda referência artificial.
        for thread, endereco in self._faltas_pendentes.pop(chave):
            fisico = moldura * self.configuracao.tamanho_pagina + endereco % self.configuracao.tamanho_pagina
            thread.tcb.registradores["endereco_fisico"] = fisico
            self._registrar("TRADUCAO_ENDERECO", thread.chave, f"lógico={endereco}; físico={fisico}")
            self._mudar_estado(thread, Estado.PRONTO, "página carregada; referência concluída")
        self._paginador_ocupado = False
        self._iniciar_paginador()

    def _executar_arquivo(self, thread: Thread, instrucao: dict) -> None:
        pcb = self.processos[thread.tcb.processo_id].pcb
        op = instrucao["op"]
        self._registrar("CHAMADA_ARQUIVO", thread.chave, repr(instrucao))
        thread.tcb.pilha_logica.append(op)
        try:
            fd = instrucao.get("fd")
            if isinstance(fd, str):
                if fd not in thread.tcb.registradores:
                    raise ErroSimulacao(f"Registrador de descritor inexistente: {fd}.")
                fd = thread.tcb.registradores[fd]
            if op in {"criar_arquivo", "criar_diretorio"}:
                self.arquivos.criar(instrucao["caminho"], op == "criar_diretorio",
                                     instrucao.get("permissoes", "rw"), self.clock)
            elif op == "abrir":
                resultado = self.arquivos.abrir(pcb, instrucao["caminho"], instrucao.get("modo", "r"), self.clock)
                thread.tcb.registradores[instrucao.get("salvar_em", "fd")] = resultado
            elif op == "escrever":
                self.arquivos.escrever(pcb, fd, instrucao["texto"], self.clock)
            elif op == "ler":
                dados = self.arquivos.ler(pcb, fd, instrucao.get("quantidade"), self.clock)
                thread.tcb.registradores["ultima_leitura"] = dados.decode("utf-8", errors="replace")
            elif op == "fechar":
                self.arquivos.fechar(pcb, fd, self.clock)
            elif op == "remover":
                self.arquivos.remover(instrucao["caminho"], self.clock)
            elif op == "listar":
                thread.tcb.registradores["ultima_listagem"] = self.arquivos.listar(instrucao["caminho"], self.clock)
            thread.tcb.registradores["erro_arquivo"] = None
        except ErroSimulacao as erro:
            thread.tcb.registradores["erro_arquivo"] = str(erro)
            self._registrar("ERRO_ARQUIVO", thread.chave, str(erro))
        finally:
            thread.tcb.pilha_logica.pop()

    def metricas(self) -> dict:
        total = self.clock
        threads = []
        processos = []
        for processo in self.processos.values():
            pcb = processo.pcb
            primeiras = [t.tcb.primeira_cpu for t in processo.threads if t.tcb.primeira_cpu is not None]
            processos.append({"processo": pcb.identificador,
                              "retorno": pcb.finalizacao - pcb.chegada,
                              "espera_threads": sum(t.tcb.tempo_espera for t in processo.threads),
                              "resposta": min(primeiras) - pcb.chegada if primeiras else None})
            for thread in processo.threads:
                tcb = thread.tcb
                threads.append({"thread": thread.chave, "retorno": tcb.finalizacao - pcb.chegada,
                                "espera": tcb.tempo_espera,
                                "resposta": tcb.primeira_cpu - pcb.chegada if tcb.primeira_cpu is not None else None,
                                "cpu": tcb.tempo_cpu})
        return {
            "tempo_total": total, "cpu_util": self.tempo_cpu,
            "utilizacao_cpu": self.tempo_cpu / total if total else 0,
            "trocas_contexto": self.trocas_contexto, "tempo_contexto": self.tempo_contexto,
            "sobrecarga_cpu": self.tempo_contexto / total if total else 0,
            "cpu_ociosa": total - self.tempo_cpu - self.tempo_contexto,
            "throughput": len(self.processos) / total if total else 0,
            "referencias_memoria": self.memoria.referencias, "acertos_memoria": self.memoria.acertos,
            "faltas_pagina": self.memoria.faltas,
            "taxa_faltas": self.memoria.faltas / self.memoria.referencias if self.memoria.referencias else 0,
            "dispositivos": {nome: {"utilizacao": d.tempo_ocupado / total if total else 0,
                                    "tempo_ocupado": d.tempo_ocupado, "concluidas": d.concluidas}
                              for nome, d in self.dispositivos.items()},
            "processos": processos, "threads": threads,
            "erros_arquivos": sum(r.tipo == "ERRO_ARQUIVO" for r in self.log.registros),
        }
