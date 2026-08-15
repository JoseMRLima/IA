
import json

import estatisticas
from Cidade import TipoGrafo
from TaxiGreenGestor import TaxiGreenGestor
from Veiculo import TipoMotorizacao, Veiculo
from Localizacao import Localizacao
from Cidade import Graph

STATSFILENAME = "data/estatisticas.json"

def carregar_veiculos(filename : str, localizacao_inicial):
    with open(filename, "r") as file:
        veiculos_init = json.load(file)

    veiculos = list()
    for obj in veiculos_init:
        if obj["tipo"]:
            tipo = TipoMotorizacao.ELETRICO
        else:
            tipo = TipoMotorizacao.COMBUSTAO

        c = Veiculo(matricula=obj["matricula"],
                    marca=obj["marca"],
                    modelo=obj["modelo"],
                    motorizacao=tipo,
                    autonomia_maxima=obj["autonomia_maxima"],
                    nr_passageiros=obj["nr_passageiros"],
                    custo_op_km=obj["custo_operacional_km"],
                    tempo_abastecer=obj["tempo_abastecer"],
                    localizacao=localizacao_inicial,
                    emissao_CO2=obj["emissao_CO2"])
        veiculos.append(c)
    return veiculos


def carregar_localizacoes(filename : str):
    with open(filename, "r") as file:
        localizacoes_init = json.load(file)

    localizacoes = list()
    for obj in localizacoes_init:
        posicao = obj["x"], obj["y"]
        l = Localizacao(nome=obj["nome"],
                        posto_recarga=obj["posto_recarga"],
                        bomba_combustivel=obj["bomba_combustivel"],
                        numero_lugares=obj["nr_lugares"],
                        posicao=posicao)
        localizacoes.append(l)

    return localizacoes


def carregar_cidade(filename : str, locais : list):
    with open(filename, "r") as file:
        cidade_init = json.load(file)

    cidade = Graph(locais)
    for obj in cidade_init:
        cidade.add_edge(obj["from"], obj["to"], [obj["distance"], obj["time"]])

    return cidade


def aplicar_algoritmo(nomes_locais, veiculos, cidade):
    choice = -1
    while choice != 0:

        print("==== Taxi Green ====")
        print("1 - Depth First")
        print("2 - Breadth First")
        print("3 - Uniform Cost")
        print("4 - Greedy Search")
        print("5 - A* Search")
        print("0 - Sair")

        alg = input("Algoritmo: ")

        if not alg.isdigit():
            print("Input inválido, tente novamente.")
            continue

        choice = int(alg)

        if choice == 0:
            break
        elif choice == 1:
            tipo = TipoGrafo.DEPTH_FIRST
        elif choice == 2:
            tipo = TipoGrafo.BREADTH_FIRST
        elif choice == 3:
            tipo = TipoGrafo.UNIFORM_COST
        elif choice == 4:
            tipo = TipoGrafo.GREEDY_SEARCH
        elif choice == 5:
            tipo = TipoGrafo.A_STAR_SEARCH
        else:
            print("Input inválido, tente novamente")
            choice = -1
            continue

        nr_pedidos = 0
        while nr_pedidos <= 0:
            out = input("Número de pedidos a resolver: ")
            if not out.isdigit():
                print("Input inválido, tente novamente")
                continue
            nr_pedidos = int(out)

        gestor = TaxiGreenGestor(tipo, nomes_locais, veiculos, cidade, nr_pedidos)
        gestor.start()


def main():

    locais_filename = "data/localizacoes.json"
    cidade_filename = "data/cidade.json"
    veiculos_filename = "data/veiculos.json"

    locais = carregar_localizacoes(locais_filename)
    cidade = carregar_cidade(cidade_filename, locais)
    veiculos = carregar_veiculos(veiculos_filename, "Central de Táxis")

    with open(STATSFILENAME, "w") as f:
        json.dump([], f)

    nomes_locais = []
    for l in locais:
        nomes_locais.append(l.nome)

    choice = -1
    while choice != 0:
        print("==== Taxi Green ====")
        print("1 - Aplicar Algoritmo")
        print("2 - Estatisticas")
        print("3 - Mapa")
        print("0 - Sair")

        op = input("Opção: ")

        if not op.isdigit():
            print("Input inválido, tente novamente.")
            continue

        choice = int(op)

        if choice == 0:
            print("A encerrar...")
            exit(1)
        elif choice == 1:
            aplicar_algoritmo(nomes_locais, veiculos, cidade)
        elif choice == 2:
            estatisticas.mostrar_estatisticas()
            continue
        elif choice == 3:
            cidade.draw()
            continue
        else:
            print("Input inválido, tente novamente")
            choice = -1
            continue

if __name__ == '__main__':
    main()
