import random
from collections import deque
from datetime import datetime, timedelta

from Pedido import Pedido, Preferencia
from Pedido import PrioridadePedido
from Veiculo import TipoMotorizacao


class GestorPedidos:

    def __init__(self, cidades : list):
        # lista de strings
        self.cidades = cidades
        self.pedidos_premium = deque()
        self.pedidos_normais = deque()
        self.instante = None

    def nr_pedidos_atuais(self):
        return len(self.pedidos_normais) + len(self.pedidos_premium)

    def criar_pedido(self) -> Pedido:
        origem, destino = random.sample(self.cidades, 2)
        nr_passageiros = random.randint(1, 8)
        # 10 a 30 segundos de espera máxima
        horario = random.randint(10, 30)
        # 70% de probabilidade de ser normal
        p = random.random() < 0.7
        if p:
            prioridade = PrioridadePedido.NORMAL
        else:
            prioridade = PrioridadePedido.URGENTE

        preferencia = random.choice([Preferencia.LOW_COST, Preferencia.FAST])
        motorizacao = random.choice([TipoMotorizacao.ELETRICO, TipoMotorizacao.COMBUSTAO])
        pedido = Pedido(origem, destino, nr_passageiros, horario, prioridade, motorizacao, preferencia)

        return pedido


    def proximo_pedido(self):
        if self.instante is None or self.instante <= datetime.now():
            # altura de criar novo pedido
            novo_pedido = self.criar_pedido()
            if novo_pedido.prioridade == PrioridadePedido.URGENTE:
                self.pedidos_premium.append(novo_pedido)
            else:
                self.pedidos_normais.append(novo_pedido)

            # intervalo de 1 a 3 segundos
            delta = random.randint(1, 3)
            self.instante = datetime.now() + timedelta(seconds=delta)

        pedido = None
        if self.pedidos_premium:
            pedido = self.pedidos_premium.popleft()
        elif self.pedidos_normais:
            pedido = self.pedidos_normais.popleft()

        return pedido


    def repor_pedido(self, pedido : Pedido):
        if pedido.prioridade == PrioridadePedido.URGENTE:
            # adicionar pedido à cabeça
            self.pedidos_premium.appendleft(pedido)
        else:
            # adicionar pedido à cabeça
            self.pedidos_normais.appendleft(pedido)
