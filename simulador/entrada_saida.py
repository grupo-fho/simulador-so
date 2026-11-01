"""Dispositivos lógicos independentes; cada fila atende em FCFS."""

from collections import deque
from dataclasses import dataclass
from typing import Callable

from .eventos import AgendaEventos, RegistroEventos
from .modelo import Thread


@dataclass
class Requisicao:
    identificador: int
    thread: Thread
    bloqueante: bool
    duracao: int
    ao_concluir: Callable[[], None]


class Dispositivo:
    def __init__(self, nome: str, tipo: str, tempo_servico: int,
                 agenda: AgendaEventos, log: RegistroEventos) -> None:
        self.nome = nome
        self.tipo = tipo
        self.tempo_servico = tempo_servico
        self.agenda = agenda
        self.log = log
        self.fila: deque[Requisicao] = deque()
        self.em_atendimento: Requisicao | None = None
        self.tempo_ocupado = 0
        self.concluidas = 0

    def solicitar(self, requisicao: Requisicao, clock: int) -> None:
        self.fila.append(requisicao)
        self.log.registrar(clock, "SOLICITACAO_ES", requisicao.thread.chave,
                           f"{self.nome}; requisição={requisicao.identificador}; bloqueante={requisicao.bloqueante}")
        if self.em_atendimento is None:
            self._iniciar_proxima(clock)

    def _iniciar_proxima(self, clock: int) -> None:
        if not self.fila:
            return
        requisicao = self.fila.popleft()
        self.em_atendimento = requisicao
        self.log.registrar(clock, "INICIO_ES", self.nome,
                           f"requisição={requisicao.identificador}; thread={requisicao.thread.chave}")
        fim = clock + requisicao.duracao
        self.agenda.agendar(fim, "CONCLUSAO_ES", lambda: self._concluir(fim))

    def _concluir(self, clock: int) -> None:
        requisicao = self.em_atendimento
        self.tempo_ocupado += requisicao.duracao
        self.concluidas += 1
        self.em_atendimento = None
        self.log.registrar(clock, "INTERRUPCAO", self.nome,
                           f"requisição={requisicao.identificador}; thread={requisicao.thread.chave}")
        requisicao.ao_concluir()
        self._iniciar_proxima(clock)
