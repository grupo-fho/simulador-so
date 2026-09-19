#!/usr/bin/env python3
"""Experimentos controlados; somente biblioteca padrão do Python 3."""
import csv
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
CENARIOS = [
    ('politica-fcfs', 'mista', 'FCFS', 3, 4),
    ('politica-rr', 'mista', 'RR', 3, 4),
    ('politica-prioridade', 'mista', 'PRIORIDADE', 3, 4),
    ('quantum-1', 'mista', 'RR', 1, 4),
    ('quantum-6', 'mista', 'RR', 6, 4),
    ('memoria-2', 'memoria', 'FCFS', 3, 2),
    ('memoria-3', 'memoria', 'FCFS', 3, 3),
]

def ler_csv(caminho):
    with caminho.open(encoding='utf-8') as arquivo:
        return list(csv.DictReader(arquivo))

def main():
    destino = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'resultados/experimentos')
    if not destino.is_absolute():
        destino = RAIZ / destino
    if destino.exists():
        raise SystemExit(f'Use uma pasta nova para preservar resultados: {destino}')
    if not (RAIZ / 'build/classes/so/Main.class').exists():
        raise SystemExit('Compile primeiro com scripts/compilar.sh ou scripts/compilar.ps1.')
    destino.mkdir(parents=True)
    comparacoes = []
    for nome, carga, politica, quantum, molduras in CENARIOS:
        saida = destino / nome
        comando = ['java', '-cp', 'build/classes', 'so.Main', '--carga', f'cargas/{carga}.txt',
                   '--politica', politica, '--quantum', str(quantum), '--molduras', str(molduras),
                   '--troca', '1', '--pagina', '16', '--falta', '5', '--disco', '4',
                   '--terminal', '2', '--semente', '42', '--saida', str(saida)]
        subprocess.run(comando, cwd=RAIZ, check=True, stdout=subprocess.DEVNULL)
        resumo = ler_csv(saida / 'resumo.csv')[0]
        threads = ler_csv(saida / 'threads.csv')
        processos = ler_csv(saida / 'processos.csv')
        linha = {'cenario': nome, 'carga': carga, 'politica': politica, 'quantum': quantum, 'molduras': molduras, **resumo}
        for metrica in ('espera', 'resposta'):
            linha[f'media_{metrica}_threads'] = f'{sum(float(t[metrica]) for t in threads)/len(threads):.6f}'
        linha['media_retorno_processos'] = f'{sum(float(p["retorno"]) for p in processos)/len(processos):.6f}'
        comparacoes.append(linha)
        print(f'{nome}: tempo={resumo["tempo_total"]}, trocas={resumo["trocas"]}, faltas={resumo["faltas"]}')
    with (destino / 'comparacoes.csv').open('w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=comparacoes[0].keys())
        escritor.writeheader()
        escritor.writerows(comparacoes)
    print(f'Comparações: {destino / "comparacoes.csv"}')

if __name__ == '__main__':
    main()
