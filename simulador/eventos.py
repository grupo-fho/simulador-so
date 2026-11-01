"""Agenda estável: empates seguem a ordem de inserção dos eventos."""

from dataclasses import dataclass, field
from heapq import heappop, heappush
from itertools import count
from typing import Callable


@dataclass(order=True)
class Evento:
    instante: int
    ordem: int
    tipo: str = field(compare=False)
    acao: Callable[[], None] = field(compare=False, repr=False)


class AgendaEventos:
    def __init__(self) -> None:
        self._eventos: list[Evento] = []
        self._sequencia = count()

    def agendar(self, instante: int, tipo: str, acao: Callable[[], None]) -> None:
        heappush(self._eventos, Evento(instante, next(self._sequencia), tipo, acao))

    def proximo(self) -> Evento:
        return heappop(self._eventos)

    @property
    def proximo_instante(self) -> int | None:
        return self._eventos[0].instante if self._eventos else None

    def __bool__(self) -> bool:
        return bool(self._eventos)


@dataclass(frozen=True)
class RegistroEvento:
    clock: int
    tipo: str
    objeto: str
    descricao: str

    def __str__(self) -> str:
        return f"[{self.clock:05d}] {self.tipo:<22} {self.objeto:<18} {self.descricao}"


class RegistroEventos:
    def __init__(self) -> None:
        self.registros: list[RegistroEvento] = []

    def registrar(self, clock: int, tipo: str, objeto: str, descricao: str) -> None:
        self.registros.append(RegistroEvento(clock, tipo, objeto, descricao))
