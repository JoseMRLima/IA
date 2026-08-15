import queue
import math
import random
import heapq

import networkx as nx
import matplotlib.pyplot as plt

from enum import Enum

from Pedido import Preferencia
from Veiculo import TipoMotorizacao


class TipoGrafo(Enum):
    BREADTH_FIRST = "BFS"
    DEPTH_FIRST = "DFS"
    UNIFORM_COST = "UNIFORM COST"
    GREEDY_SEARCH = "GREEDY"
    A_STAR_SEARCH = "A*"


class Graph:

    def __init__(self, locais : list):
        # lista de Localizacao
        self.locais = locais
        # nome localizacao -> [nome localizacao destino, [distancia, tempo segundos]]
        self.edges = dict()
        self.tipo = None


    def gerar_transito(self):
        nomes_locais = []
        for l in self.locais:
            nomes_locais.append(l.nome)

        local1 = random.choice(nomes_locais)
        adjacentes = self.edges[local1]
        local2 = random.choice(adjacentes)
        valor = random.randint(1, 5)
        if random.random() < 0.5:
            valor = valor
        else:
            if local2[1][1] > valor:
                valor = -valor
            else:
                valor = -local2[1][1] + 1

        local2[1][1] += valor


    def set_tipo(self, tipo : TipoGrafo):
        self.tipo = tipo

    def get_distance(self, src : str, dest : str) -> int:
        for node, w in self.edges[src]:
            if node == dest:
                return w[0]
        return 0

    def get_time(self, src : str, dest : str) -> int:
        for node, w in self.edges[src]:
            if node == dest:
                return w[1]
        return 0

    def add_edge(self, src : str, dest : str, weight : list):
        """
        Adiciona uma aresta ao grafo

        :param src: origem da aresta
        :param dest: destino da aresta
        :param weight: peso da aresta
        """
        if src not in self.edges:
            self.edges[src] = list()
        if dest not in self.edges:
            self.edges[dest] = list()

        self.edges[src].append([dest, weight])
        self.edges[dest].append([src, weight])

    def get_heuristic(self, src : str, dest : str):
        for l in self.locais:
            if l.nome == src:
                for d in self.locais:
                    if d == dest:
                        return math.sqrt((d.position[0] - l.position[0]) ** 2 + (d.position[1] - l.position[1]) ** 2)
                break
        return 0

    def get_edge_cost(self, src, dest):
        if random.random() < 0.01:
            # 1% de probabilidade de gerar transito
            self.gerar_transito()

        for (node_id, weight) in self.edges[src]:
            if node_id == dest:
                return weight[0], weight[1]
        return math.inf

    def get_neighbours(self, node):
        return self.edges[node]

    def get_path_cost(self, path):
        i = 0
        distancia, tempo = 0, 0
        while i + 1 < len(path):
            c = self.get_edge_cost(path[i], path[i + 1])
            # invalid path
            if c is math.inf:
                return math.inf

            # distancia
            distancia += c[0]
            # tempo
            tempo += c[1]

            i = i + 1

        return distancia, tempo

    def find_lowest_estimate(self, estimates):
        # selecionar qualquer elemento como um minimo inicial
        nodes = list(estimates.keys())
        lowest_node = nodes[0]
        lowest_value = estimates[lowest_node]

        # procurar a estimativa mais pequena
        for node, value in estimates.items():
            if value < lowest_value:
                lowest_value = value
                lowest_node = node

        return lowest_node


    def draw(self):
        """Apresenta uma representação gráfica do grafo"""
        g = nx.Graph()
        for node in self.edges:
            g.add_node(node)
            for neighbour, w in self.edges[node]:
                g.add_edge(
                    node,
                    neighbour,
                    label=f"{w[0]}m / {w[1]}seg"
                )

        posicoes = dict()
        for l in self.locais:
            posicoes[l.nome] = l.posicao

        plt.figure(figsize=(20, 14))

        pos = posicoes
        nx.draw_networkx_nodes(
            g, pos,
            node_size=1000,
            node_color="#AED6F1",
            edgecolors="#1B4F72"
        )

        nx.draw_networkx_edges(
            g, pos,
            width=2,
            alpha=0.8
        )

        nx.draw_networkx_labels(
            g, pos,
            font_size=10,
            font_weight="bold"
        )

        edge_labels = nx.get_edge_attributes(g, "label")
        nx.draw_networkx_edge_labels(
            g, pos,
            edge_labels=edge_labels,
            font_size=8,
            rotate=False
        )

        plt.axis("off")
        plt.tight_layout()
        plt.show()

    # procura não informada

    def depth_first_search(self, src, dest):
        """
        Determina se existe um caminho entre dois nodos, usando o
        algoritmo de procura em profundidade

        :param src: nodo de origem
        :param dest: nodo de destino
        :return: caminho (lista de nomes de localizacoes), None se não existir caminho
        """
        # (nó atual, caminho até ao nó)
        stack = [(src, [src])]
        visited = set()

        while stack:
            node, path = stack.pop()

            if node == dest:
                return path

            if node not in visited:
                visited.add(node)

                for (neighbor, _) in self.edges[node]:
                    if neighbor not in visited:
                        stack.append((neighbor, path + [neighbor]))

        return None


    def breadth_first_search(self, src, dest):
        """
        Determina se existe um caminho entre dois nodos, usando o
        algoritmo de procura em largura

        :param src: nodo de origem
        :param dest: nodo de destino
        :return: caminho (lista de nomes de localizacoes), None se não existir caminho
        """
        # nodos visitados
        visited = set()
        # fila dos nodos a visitar
        to_visit = queue.Queue()

        to_visit.put(src)
        visited.add(src)

        # dicionario para reconstruir caminho
        parent = dict()
        parent[src] = None

        if src == dest:
            return [src]

        path_found = False
        while not to_visit.empty() and path_found == False:
            current = to_visit.get()

            # percorrer nodos adjacentes
            for (neighbour, weight) in self.edges[current]:
                if neighbour not in visited:
                    to_visit.put(neighbour)
                    parent[neighbour] = current
                    visited.add(neighbour)
                    # destino encontrado
                    # evita expansões desnecessárias
                    if neighbour == dest:
                        path_found = True
                        break

        # reconstruir o caminho
        if path_found:
            path = [dest]
            while parent[dest] is not None:
                path.append(parent[dest])
                dest = parent[dest]
            path.reverse()

            return path
        else:
            return None

    def uniform_cost_search(self, src : str, dest : str, preferencia):
        frontier = []
        heapq.heappush(frontier, (0, src))
        cost_so_far = {src: 0}
        parents = {src: None}

        while frontier:
            current_cost, current = heapq.heappop(frontier)

            if current == dest:
                path = []
                while current is not None:
                    path.append(current)
                    current = parents[current]
                return list(reversed(path))

            for neighbour, _ in self.get_neighbours(current):
                if preferencia == Preferencia.LOW_COST:
                    cost = self.get_distance(current, neighbour)
                else:
                    cost = self.get_time(current, neighbour)
                new_cost = current_cost + cost
                if neighbour not in cost_so_far or new_cost < cost_so_far[neighbour]:
                    cost_so_far[neighbour] = new_cost
                    parents[neighbour] = current
                    heapq.heappush(frontier, (new_cost, neighbour))

        return None


    # procura informada

    def greedy_search(self, src, dest):
        """
        Determina se existe um caminho entre dois nodos, usando o
        algoritmo de procura gulosa

        :param src: nodo de origem
        :param dest: nodo de destino
        :return: caminho (lista de nomes de localizacoes), None se não existir caminho
        """
        # nodos visitados, mas com vizinhos por visitar
        open_list = set()
        open_list.add(src)

        # nodos visitados, nos quais os vizinhos foram visitados tambem
        closed_list = set()

        # dicionario para reconstruir caminho
        parents = dict()
        parents[src] = src

        while len(open_list) > 0:
            current = None

            # selecionar nodo com a menor heuristica
            for v in open_list:
                if current is None or self.get_heuristic(src, v) < self.get_heuristic(src, current):
                    current = v

            if current is None:
                return None

            # nodo atual é o destino
            if current == dest:
                # reconstruir o caminho
                reconst_path = []
                while parents[current] != current:
                    reconst_path.append(current)
                    current = parents[current]
                reconst_path.append(src)
                reconst_path.reverse()

                return reconst_path

            # percorrer vizinhos do nodo atual
            for neighbour, weight in self.edges[current]:
                if neighbour not in open_list and neighbour not in closed_list:
                    open_list.add(neighbour)
                    parents[neighbour] = current

            # remover o nodo atual da open_list e adiciona-lo à closed_list
            # porque todos os seus vizinhos foram inspecionados
            open_list.remove(current)
            closed_list.add(current)

        return None


    def a_star_search(self, src, dest, preferencia):
        # nodos visitados, mas com vizinhos por visitar
        open_list = set()
        open_list.add(src)

        # nodos visitados, nos quais os vizinhos foram visitados tambem
        closed_list = set()

        # guarda o custo do caminho de um nodo até src
        # valor por defeito é +infinity
        cost_so_far = dict()
        cost_so_far[src] = 0

        # dicionario para reconstruir caminho
        parents = dict()
        parents[src] = src

        current = None
        while len(open_list) > 0:
            # valores da função de avaliação dos nodos com potencial
            calc_heurist = dict()
            flag = 0

            # calcular os custos dos nodos com potencial
            for visited in open_list:
                if current is None:
                    current = visited
                else:
                    flag = 1
                    calc_heurist[visited] = cost_so_far[visited] + self.get_heuristic(src, visited)

            # procurar o nodo com menor estimativa de custo
            if flag == 1:
                current = self.find_lowest_estimate(calc_heurist)

            if current is None:
                return None

            # nodo atual é o destino
            if current == dest:
                # reconstruir o caminho
                reconst_path = []
                while parents[current] != current:
                    reconst_path.append(current)
                    current = parents[current]
                reconst_path.append(src)
                reconst_path.reverse()

                return reconst_path

            # percorrer vizinhos do nodo atual
            for (neighbour, weight) in self.get_neighbours(current):
                if neighbour not in open_list and neighbour not in closed_list:
                    open_list.add(neighbour)
                    parents[neighbour] = current
                    if preferencia == Preferencia.LOW_COST:
                        d = self.get_distance(current, neighbour)
                        cost_so_far[neighbour] = cost_so_far[current] + d
                    else:
                        t = self.get_time(current, neighbour)
                        cost_so_far[neighbour] = cost_so_far[current] + t
                else:
                    if preferencia == Preferencia.LOW_COST:
                        w = self.get_distance(current, neighbour)
                    else:
                        w = self.get_time(current, neighbour)
                    # verificar se neighbour é uma alternativa melhor
                    if cost_so_far[neighbour] > cost_so_far[current] + w:
                        cost_so_far[neighbour] = cost_so_far[current] + w
                        parents[neighbour] = current

                        # colocar neighbour na open_list
                        if neighbour in closed_list:
                            closed_list.remove(neighbour)
                            open_list.add(neighbour)

            # remover o nodo atual da open_list e adiciona-lo à closed_list
            # porque todos os seus vizinhos foram inspecionados
            open_list.remove(current)
            closed_list.add(current)

        return None


    def is_posto(self, local : str, tipo):
        for l in self.locais:
            if l.nome == local:
                if tipo == TipoMotorizacao.ELETRICO and l.posto_recarga:
                    return l.tem_lugar_disponivel()
                if tipo == TipoMotorizacao.COMBUSTAO and l.bomba_combustivel:
                    return l.tem_lugar_disponivel()
        return False

    def depth_first_search_posto(self, src : str, tipo : TipoMotorizacao):
        # (nó atual, caminho até ao nó)
        stack = [(src, [src])]
        visited = set()

        while stack:
            node, path = stack.pop()

            if self.is_posto(node, tipo):
                return path

            if node not in visited:
                visited.add(node)

                for (neighbor, _) in self.edges[node]:
                    if neighbor not in visited:
                        stack.append((neighbor, path + [neighbor]))

        return None


    def procurar_posto(self, origem : str, tipo : TipoMotorizacao):
        ls = []
        for local in self.locais:
            if ((tipo == TipoMotorizacao.ELETRICO and local.posto_recarga)
                    or (tipo == TipoMotorizacao.COMBUSTAO and local.bomba_combustivel)):
                if local.tem_lugar_disponivel:
                    # calcular caminho, distancia e tempo
                    out = self.search(origem, local.nome, Preferencia.LOW_COST)
                    if out is not None:
                        distancia, tempo = out[0], out[1]
                        ls.append([local, distancia, tempo])

        if len(ls) == 0:
            return None
        else:
            # selecionar o posto mais perto
            l, d, t = min(ls, key=lambda x: x[1])
            return l.nome, d, t


    def abastecer_veiculo(self, posto : str, tempo : int):
        for l in self.locais:
            if l.nome == posto:
                l.ocupar_lugar(tempo)
                break


    def search(self, src, dest, preferencia):
        if self.tipo == TipoGrafo.DEPTH_FIRST:
            caminho = self.depth_first_search(src, dest)
        elif self.tipo == TipoGrafo.BREADTH_FIRST:
            caminho = self.breadth_first_search(src, dest)
        elif self.tipo == TipoGrafo.GREEDY_SEARCH:
            caminho = self.greedy_search(src, dest)
        elif self.tipo == TipoGrafo.A_STAR_SEARCH:
            caminho = self.a_star_search(src, dest, preferencia)
        else:
            caminho = self.uniform_cost_search(src, dest, preferencia)

        if caminho is not None:
            return self.get_path_cost(caminho)
        return None
