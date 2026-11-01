"""O mecanismo mantém a fila; as políticas decidem quem sai dela."""

from abc import ABC, abstractmethod

from .modelo import Thread


class PoliticaEscalonamento(ABC):
    @abstractmethod
    def selecionar(self, fila: list[Thread], prioridades: dict[str, int]) -> int:
        """Retorna o índice da próxima thread, sem alterar a fila."""


class FCFS(PoliticaEscalonamento):
    def selecionar(self, fila: list[Thread], prioridades: dict[str, int]) -> int:
        return 0


class RoundRobin(FCFS):
    """Mesma seleção FCFS; o núcleo devolve a thread ao fim após o quantum."""


class Prioridades(PoliticaEscalonamento):
    """Não preemptiva; menor número significa maior prioridade."""

    def selecionar(self, fila: list[Thread], prioridades: dict[str, int]) -> int:
        return min(range(len(fila)), key=lambda i: prioridades[fila[i].tcb.processo_id])


class Escalonador:
    def __init__(self, algoritmo: str, prioridades: dict[str, int]) -> None:
        self.politica = {"fcfs": FCFS, "rr": RoundRobin, "prioridades": Prioridades}[algoritmo]()
        self.prioridades = prioridades
        self.fila_prontos: list[Thread] = []

    def adicionar(self, thread: Thread) -> None:
        if thread in self.fila_prontos:
            raise RuntimeError(f"Thread duplicada na fila: {thread.chave}")
        self.fila_prontos.append(thread)

    def selecionar(self) -> Thread:
        indice = self.politica.selecionar(self.fila_prontos, self.prioridades)
        return self.fila_prontos.pop(indice)
