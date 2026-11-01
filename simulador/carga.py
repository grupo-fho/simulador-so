"""Valida uma carga textual antes de criar qualquer recurso da simulação."""

import json
from pathlib import Path

from .modelo import ErroSimulacao, EspacoEnderecamento, PCB, Processo, TCB, Thread


def inteiro(valor: object, contexto: str, minimo: int = 0) -> int:
    if type(valor) is not int or valor < minimo:
        raise ErroSimulacao(f"{contexto}: esperado inteiro >= {minimo}.")
    return valor


def texto(valor: object, contexto: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ErroSimulacao(f"{contexto}: esperado texto não vazio.")
    return valor


def validar_instrucao(instrucao: object, tamanho_memoria: int, contexto: str) -> dict:
    if not isinstance(instrucao, dict):
        raise ErroSimulacao(f"{contexto}: instrução deve ser um objeto JSON.")
    operacao = instrucao.get("op")
    campos = {
        "cpu": {"duracao"}, "memoria": {"endereco"},
        "es": {"dispositivo", "bloqueante", "duracao"},
        "criar_arquivo": {"caminho", "permissoes"},
        "criar_diretorio": {"caminho", "permissoes"},
        "abrir": {"caminho", "modo", "salvar_em"},
        "ler": {"fd", "quantidade"}, "escrever": {"fd", "texto"},
        "fechar": {"fd"}, "remover": {"caminho"}, "listar": {"caminho"},
    }
    if not isinstance(operacao, str) or operacao not in campos:
        raise ErroSimulacao(f"{contexto}: operação desconhecida {operacao!r}.")
    desconhecidos = set(instrucao) - campos[operacao] - {"op"}
    if desconhecidos:
        raise ErroSimulacao(f"{contexto}: campos desconhecidos {sorted(desconhecidos)}.")
    if operacao == "cpu":
        inteiro(instrucao.get("duracao"), contexto + ".duracao", 1)
    if operacao == "memoria":
        endereco = inteiro(instrucao.get("endereco"), contexto + ".endereco")
        if endereco >= tamanho_memoria:
            raise ErroSimulacao(f"{contexto}: endereço fora do espaço lógico.")
    if operacao == "es":
        if instrucao.get("dispositivo") not in ("disco", "terminal"):
            raise ErroSimulacao(f"{contexto}: dispositivo deve ser disco ou terminal.")
        if type(instrucao.get("bloqueante", True)) is not bool:
            raise ErroSimulacao(f"{contexto}: bloqueante deve ser booleano.")
        if "duracao" in instrucao:
            inteiro(instrucao["duracao"], contexto + ".duracao", 1)
    if "caminho" in campos[operacao]:
        caminho = texto(instrucao.get("caminho"), contexto + ".caminho")
        if not caminho.startswith("/"):
            raise ErroSimulacao(f"{contexto}: caminho deve começar por /.")
    if "permissoes" in instrucao and instrucao["permissoes"] not in ("r", "w", "rw", ""):
        raise ErroSimulacao(f"{contexto}: permissões inválidas.")
    if operacao == "abrir":
        if instrucao.get("modo", "r") not in ("r", "w", "rw", "a"):
            raise ErroSimulacao(f"{contexto}: modo de abertura inválido.")
        texto(instrucao.get("salvar_em", "fd"), contexto + ".salvar_em")
    if "fd" in campos[operacao]:
        descritor = instrucao.get("fd")
        if isinstance(descritor, str):
            texto(descritor, contexto + ".fd")
        else:
            inteiro(descritor, contexto + ".fd")
    if "quantidade" in instrucao:
        inteiro(instrucao["quantidade"], contexto + ".quantidade")
    if operacao == "escrever" and not isinstance(instrucao.get("texto"), str):
        raise ErroSimulacao(f"{contexto}: texto de escrita deve ser string.")
    return instrucao.copy()


def construir_processos(dados: object) -> list[Processo]:
    if not isinstance(dados, dict) or set(dados) != {"processos"}:
        raise ErroSimulacao("A raiz JSON deve conter somente a lista 'processos'.")
    if not isinstance(dados["processos"], list) or not dados["processos"]:
        raise ErroSimulacao("A carga precisa de pelo menos um processo.")
    processos = []
    identificadores = set()
    for item in dados["processos"]:
        if not isinstance(item, dict):
            raise ErroSimulacao("Processo deve ser um objeto JSON.")
        if set(item) - {"id", "chegada", "prioridade", "memoria", "threads"}:
            raise ErroSimulacao("Processo contém campos desconhecidos.")
        identificador = texto(item.get("id"), "processo.id")
        if "/" in identificador or identificador in identificadores:
            raise ErroSimulacao("IDs de processo devem ser únicos e não conter /.")
        identificadores.add(identificador)
        chegada = inteiro(item.get("chegada"), f"{identificador}.chegada")
        prioridade = inteiro(item.get("prioridade"), f"{identificador}.prioridade")
        memoria = inteiro(item.get("memoria", 256), f"{identificador}.memoria", 1)
        definicoes = item.get("threads")
        if not isinstance(definicoes, list) or not definicoes:
            raise ErroSimulacao(f"{identificador}: informe uma ou mais threads.")
        threads = []
        ids_threads = set()
        for definicao in definicoes:
            if not isinstance(definicao, dict) or set(definicao) != {"id", "instrucoes"}:
                raise ErroSimulacao("Thread deve conter id e instrucoes.")
            tid = texto(definicao["id"], "thread.id")
            if tid in ids_threads or "/" in tid:
                raise ErroSimulacao(f"IDs de thread inválidos ou repetidos em {identificador}.")
            ids_threads.add(tid)
            instrucoes = definicao["instrucoes"]
            if not isinstance(instrucoes, list) or not instrucoes:
                raise ErroSimulacao(f"{identificador}/{tid}: instrucoes deve ser lista não vazia.")
            validadas = [validar_instrucao(i, memoria, f"{identificador}/{tid}[{n}]")
                         for n, i in enumerate(instrucoes)]
            threads.append(Thread(TCB(tid, identificador), validadas))
        pcb = PCB(identificador, prioridade, chegada, EspacoEnderecamento(memoria),
                  threads=[thread.tcb.identificador for thread in threads])
        processos.append(Processo(pcb, threads))
    return processos


def carregar_texto(conteudo: str) -> list[Processo]:
    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError as erro:
        raise ErroSimulacao(f"JSON inválido na linha {erro.lineno}, coluna {erro.colno}: {erro.msg}.") from erro
    return construir_processos(dados)


def carregar_arquivo(caminho: str) -> list[Processo]:
    # Somente leitura de um cenário; não é persistência dos arquivos simulados.
    return carregar_texto(Path(caminho).read_text(encoding="utf-8-sig"))
