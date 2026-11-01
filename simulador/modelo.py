"""Entidades do modelo, sem dependência da interface de terminal."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ErroSimulacao(ValueError):
    """Uma solicitação viola as regras do sistema simulado."""


class Estado(str, Enum):
    NOVO = "novo"
    PRONTO = "pronto"
    EXECUTANDO = "executando"
    BLOQUEADO = "bloqueado"
    FINALIZADO = "finalizado"


@dataclass
class EntradaPagina:
    presente: bool = False
    moldura: int | None = None


@dataclass
class EspacoEnderecamento:
    tamanho: int
    tabela_paginas: dict[int, EntradaPagina] = field(default_factory=dict)


@dataclass
class PCB:
    identificador: str
    prioridade: int
    chegada: int
    espaco_enderecamento: EspacoEnderecamento
    estado: Estado = Estado.NOVO
    contador_programa: int = 0
    registradores: dict[str, Any] = field(default_factory=dict)
    threads: list[str] = field(default_factory=list)
    arquivos_abertos: dict[int, int] = field(default_factory=dict)
    finalizacao: int | None = None


@dataclass
class TCB:
    identificador: str
    processo_id: str
    estado: Estado = Estado.NOVO
    contador_programa: int = 0
    registradores: dict[str, Any] = field(default_factory=dict)
    pilha_logica: list[str] = field(default_factory=list)
    notificacoes: list[str] = field(default_factory=list)
    cpu_restante: int = 0
    quantum_restante: int = 0
    entrada_prontos: int = 0
    tempo_espera: int = 0
    tempo_cpu: int = 0
    primeira_cpu: int | None = None
    finalizacao: int | None = None


@dataclass
class Thread:
    tcb: TCB
    instrucoes: list[dict[str, Any]]

    @property
    def chave(self) -> str:
        return f"{self.tcb.processo_id}/{self.tcb.identificador}"


@dataclass
class Processo:
    pcb: PCB
    threads: list[Thread]
