"""Paginação com substituição global FIFO; o núcleo agenda o atendimento."""

from collections import deque

from .modelo import EntradaPagina, ErroSimulacao, Processo


class GerenciadorMemoria:
    def __init__(self, tamanho_pagina: int, numero_molduras: int,
                 processos: dict[str, Processo]) -> None:
        self.tamanho_pagina = tamanho_pagina
        self.molduras: list[tuple[str, int] | None] = [None] * numero_molduras
        self.ordem_fifo: deque[int] = deque()
        self.processos = processos
        self.referencias = 0
        self.acertos = 0
        self.faltas = 0

    def decompor_endereco(self, processo_id: str, endereco: int) -> tuple[int, int]:
        espaco = self.processos[processo_id].pcb.espaco_enderecamento
        if type(endereco) is not int or not 0 <= endereco < espaco.tamanho:
            raise ErroSimulacao(f"Endereço {endereco} fora do espaço de {processo_id}.")
        return divmod(endereco, self.tamanho_pagina)

    def acessar(self, processo_id: str, endereco: int) -> int | None:
        pagina, deslocamento = self.decompor_endereco(processo_id, endereco)
        tabela = self.processos[processo_id].pcb.espaco_enderecamento.tabela_paginas
        entrada = tabela.setdefault(pagina, EntradaPagina())
        self.referencias += 1
        if entrada.presente:
            self.acertos += 1
            return entrada.moldura * self.tamanho_pagina + deslocamento
        self.faltas += 1
        return None

    def carregar(self, processo_id: str, pagina: int) -> tuple[int, tuple[str, int] | None]:
        tabela = self.processos[processo_id].pcb.espaco_enderecamento.tabela_paginas
        entrada = tabela.setdefault(pagina, EntradaPagina())
        if entrada.presente:
            return entrada.moldura, None
        vitima = None
        if None in self.molduras:
            moldura = self.molduras.index(None)
        else:
            moldura = self.ordem_fifo.popleft()
            vitima = self.molduras[moldura]
            entrada_vitima = self.processos[vitima[0]].pcb.espaco_enderecamento.tabela_paginas[vitima[1]]
            entrada_vitima.presente = False
            entrada_vitima.moldura = None
        self.molduras[moldura] = (processo_id, pagina)
        self.ordem_fifo.append(moldura)
        entrada.presente = True
        entrada.moldura = moldura
        return moldura, vitima

    def liberar(self, processo_id: str) -> None:
        for indice, pagina in enumerate(self.molduras):
            if pagina is not None and pagina[0] == processo_id:
                self.molduras[indice] = None
                self.ordem_fifo.remove(indice)
        self.processos[processo_id].pcb.espaco_enderecamento.tabela_paginas.clear()
