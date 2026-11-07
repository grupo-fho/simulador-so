"""Interface textual: lê cenários e apresenta resultados sem salvar a execução."""

import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path
import sys

from .carga import carregar_arquivo, carregar_texto
from .configuracao import Configuracao
from .modelo import ErroSimulacao
from .nucleo import Simulador


PASTA_CARGAS = Path(__file__).resolve().parent.parent / "cargas"


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simulador de SO orientado a objetos; dados somente em memória.")
    parser.add_argument("--ajuda", action="help", help="mostra esta ajuda e termina")
    parser.add_argument("--interativo", action="store_true", help="abre o terminal contínuo (padrão sem argumentos)")
    origem = parser.add_mutually_exclusive_group()
    origem.add_argument("--carga", metavar="ARQUIVO", help="cenário JSON externo; use - para ler da entrada padrão")
    origem.add_argument("--cenario", choices=["cpu", "es", "mista", "verificacao", "memoria", "arquivos"],
                        default="mista", help="carga incluída na aplicação (padrão: mista)")
    parser.add_argument("--algoritmo", choices=["fcfs", "rr", "prioridades"], default="rr")
    parametros = {
        "quantum": (2, "tempo de CPU permitido por rodada RR"),
        "custo-contexto": (0, "tempo de cada despacho, incluindo o primeiro"),
        "tamanho-pagina": (16, "bytes por página e moldura"),
        "numero-molduras": (3, "capacidade da memória física"),
        "tempo-falta-pagina": (3, "serviço por carregamento, em fila FCFS"),
        "tempo-disco": (4, "serviço padrão do dispositivo de bloco"),
        "tempo-terminal": (2, "serviço padrão do dispositivo de caractere"),
        "tamanho-bloco": (16, "bytes por bloco do disco virtual"),
        "numero-blocos": (64, "capacidade do disco virtual em blocos"),
        "semente": (42, "semente registrada; as cargas fornecidas não usam aleatoriedade"),
    }
    for nome, (padrao, ajuda) in parametros.items():
        parser.add_argument("--" + nome, type=int, default=padrao, help=f"{ajuda} (padrão: {padrao})")
    parser.add_argument("--sem-log", action="store_true", help="mostra somente métricas")
    parser.add_argument("--json", action="store_true", help="emite configuração, eventos e métricas como JSON no terminal")
    parser.add_argument("--experimentos", action="store_true", help="executa três comparações reproduzíveis no terminal")
    return parser


def executar_experimentos(configuracao: Configuracao) -> list[dict]:
    """Recria os objetos em cada execução: nenhum estado passa para o próximo caso."""
    grupos = [
        ("politicas", "mista", [replace(configuracao, algoritmo=a)
                                  for a in ("fcfs", "rr", "prioridades")]),
        ("quantum", "cpu", [replace(configuracao, algoritmo="rr", quantum=q, custo_contexto=1)
                              for q in (1, 4)]),
        ("memoria", "memoria", [replace(configuracao, numero_molduras=n) for n in (2, 4)]),
    ]
    resultados = []
    for grupo, cenario, configuracoes in grupos:
        for config in configuracoes:
            simulador = Simulador(carregar_arquivo(str(PASTA_CARGAS / f"{cenario}.json")), config)
            metricas = simulador.executar()
            resultados.append({"experimento": grupo, "cenario": cenario,
                               "configuracao": asdict(config), "metricas": metricas})
    return resultados


def apresentar_metricas(metricas: dict) -> None:
    print("\nMÉTRICAS (unidades do clock lógico)")
    print(f"Tempo total: {metricas['tempo_total']} | CPU útil: {metricas['cpu_util']} "
          f"({metricas['utilizacao_cpu']:.2%}) | CPU ociosa: {metricas['cpu_ociosa']}")
    print(f"Despachos/trocas: {metricas['trocas_contexto']} | Sobrecarga: {metricas['tempo_contexto']} "
          f"({metricas['sobrecarga_cpu']:.2%}) | Throughput: {metricas['throughput']:.4f}")
    print(f"Memória: {metricas['referencias_memoria']} referências | {metricas['acertos_memoria']} acertos | "
          f"{metricas['faltas_pagina']} faltas ({metricas['taxa_faltas']:.2%})")
    for nome, dispositivo in metricas["dispositivos"].items():
        print(f"{nome}: utilização={dispositivo['utilizacao']:.2%}; "
              f"ocupação={dispositivo['tempo_ocupado']}; concluídas={dispositivo['concluidas']}")
    print("\nThread                  Retorno   Espera   Resposta   CPU")
    for thread in metricas["threads"]:
        resposta = "n/a" if thread["resposta"] is None else str(thread["resposta"])
        print(f"{thread['thread']:<24}{thread['retorno']:>7}{thread['espera']:>9}{resposta:>11}{thread['cpu']:>6}")
    print("\nProcesso                Retorno   Espera das threads   Resposta")
    for processo in metricas["processos"]:
        resposta = "n/a" if processo["resposta"] is None else str(processo["resposta"])
        print(f"{processo['processo']:<24}{processo['retorno']:>7}{processo['espera_threads']:>20}{resposta:>11}")
    print(f"Erros de chamadas de arquivos detectados: {metricas['erros_arquivos']}")


def main(argumentos: list[str] | None = None) -> int:
    argumentos = sys.argv[1:] if argumentos is None else argumentos
    parser = criar_parser()
    opcoes = parser.parse_args(argumentos)
    try:
        configuracao = Configuracao(**{nome: getattr(opcoes, nome) for nome in Configuracao.__dataclass_fields__})
        if opcoes.experimentos:
            resultados = executar_experimentos(configuracao)
            if opcoes.json:
                print(json.dumps(resultados, ensure_ascii=False, indent=2))
            else:
                for resultado in resultados:
                    print(f"\nEXPERIMENTO: {resultado['experimento']} | carga={resultado['cenario']}")
                    print("Configuração:", json.dumps(resultado["configuracao"], ensure_ascii=False))
                    apresentar_metricas(resultado["metricas"])
            return 0
        if opcoes.carga == "-":
            processos = carregar_texto(sys.stdin.read())
        else:
            caminho = opcoes.carga or str(PASTA_CARGAS / f"{opcoes.cenario}.json")
            processos = carregar_arquivo(caminho)
        simulador = Simulador(processos, configuracao)
        if not argumentos or opcoes.interativo:
            from .shell import Shell
            return Shell(simulador).executar()
        metricas = simulador.executar()
        if opcoes.json:
            print(json.dumps({"configuracao": asdict(configuracao),
                              "eventos": [] if opcoes.sem_log else [asdict(r) for r in simulador.log.registros],
                              "metricas": metricas}, ensure_ascii=False, indent=2))
        else:
            if opcoes.sem_log:
                print("Configuração:", json.dumps(asdict(configuracao), ensure_ascii=False))
            else:
                for registro in simulador.log.registros:
                    print(registro)
            apresentar_metricas(metricas)
        return 0
    except (ErroSimulacao, OSError, UnicodeError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 2
