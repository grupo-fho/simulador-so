from dataclasses import dataclass

from .modelo import ErroSimulacao


@dataclass(frozen=True)
class Configuracao:
    algoritmo: str = "rr"
    quantum: int = 2
    custo_contexto: int = 0
    tamanho_pagina: int = 16
    numero_molduras: int = 3
    tempo_falta_pagina: int = 3
    tempo_disco: int = 4
    tempo_terminal: int = 2
    tamanho_bloco: int = 16
    numero_blocos: int = 64
    semente: int = 42

    def __post_init__(self) -> None:
        if self.algoritmo not in {"fcfs", "rr", "prioridades"}:
            raise ErroSimulacao("Algoritmo deve ser fcfs, rr ou prioridades.")
        for nome in ("quantum", "tamanho_pagina", "numero_molduras", "tempo_falta_pagina",
                     "tempo_disco", "tempo_terminal", "tamanho_bloco", "numero_blocos"):
            valor = getattr(self, nome)
            if type(valor) is not int or valor <= 0:
                raise ErroSimulacao(f"{nome} deve ser um inteiro positivo.")
        if type(self.custo_contexto) is not int or self.custo_contexto < 0:
            raise ErroSimulacao("custo_contexto deve ser um inteiro não negativo.")
        if type(self.semente) is not int:
            raise ErroSimulacao("semente deve ser inteira.")
