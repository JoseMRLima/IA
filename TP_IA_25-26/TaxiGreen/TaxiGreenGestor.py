
from datetime import datetime, timedelta
import json

from Cidade import TipoGrafo
from Pedido import Pedido, EstadoPedido, Preferencia
from Veiculo import Veiculo
from Cidade import Graph
from GestorPedidos import GestorPedidos

STATSFILENAME = "data/estatisticas.json"

class TaxiGreenGestor:

    def __init__(self, tipo : TipoGrafo, locais : list, veiculos : list, cidade : Graph, nr_pedidos : int):
        self.tipo = tipo
        self.gestor_pedidos = GestorPedidos(locais)
        self.veiculos = veiculos
        self.cidade = cidade
        self.cidade.set_tipo(self.tipo)
        self.pedidos_resolvidos = []
        self.dist_s_pass = 0
        self.custo_op_total = 0
        self.nr_ped_rej = 0
        self.nr_pedidos = nr_pedidos
        self.veiculos_bloqueados = []
        self.perc_lugares = []
        self.taxa_ocupacao = []
        self.count_taxa_ocu = 0
        self.instante_registo_taxa = None
        self.emissao_CO2_total = 0

    def abastecer_veiculo(self, veiculo : Veiculo):
        # procurar o melhor posto de combustivel/recarga dado um local
        posto, distancia, tempo = self.cidade.procurar_posto(veiculo.localizacao, veiculo.motorizacao)
        if veiculo.pode_fazer_viagem(distancia):
            # colocar um lugar a menos livre no posto
            self.cidade.abastecer_veiculo(posto, tempo + veiculo.tempo_abastecer)
            veiculo.abastecer(posto, tempo)
        else:
            # adicionar veiculo à lista de veiculos bloqueados
            if veiculo.matricula not in self.veiculos_bloqueados:
                self.veiculos_bloqueados.append(veiculo)
                self.veiculos.remove(veiculo)


    def resolver_pedido(self, pedido : Pedido):
        # calcular distancia e tempo de viagem do pedido
        distancia, tempo = self.cidade.search(pedido.origem, pedido.destino, pedido.preferencia)

        melhor_carro = None
        melhor_distancia = 0
        melhor_tempo = 0

        for v in self.veiculos:
            if v.motorizacao == pedido.motorizacao and v.disponivel():
                # veiculo disponivel
                if v.precisa_abastecer():
                    # necessita de abastecer
                    self.abastecer_veiculo(v)
                else:
                    local_atual = v.localizacao

                    out_origem = self.cidade.search(local_atual, pedido.origem, pedido.preferencia)
                    # existe caminho entre localização do veiculo e origem do pedido
                    distancia_origem, tempo_origem = out_origem[0], out_origem[1]
                    if pedido.numero_passageiros <= v.nr_passageiros and v.pode_fazer_viagem(distancia_origem + distancia):
                        if pedido.preferencia == Preferencia.LOW_COST:
                            if melhor_carro is None or (v.custo_op_km * distancia_origem < melhor_carro.custo_op_km * melhor_distancia):
                                melhor_carro = v
                                melhor_distancia = distancia_origem
                                melhor_tempo = tempo_origem
                        else:
                            if melhor_carro is None or tempo_origem < melhor_tempo:
                                melhor_carro = v
                                melhor_distancia = distancia_origem
                                melhor_tempo = tempo_origem

        if melhor_carro is not None:
            pedido.tempo_total = tempo + melhor_tempo
            pedido.distancia_total = distancia + melhor_distancia
            tempo_resposta = (datetime.now() - pedido.instante_criacao).total_seconds()
            pedido.tempo_resposta = tempo_resposta
            pedido.estado = EstadoPedido.REALIZADO

            self.perc_lugares.append((pedido.numero_passageiros / melhor_carro.nr_passageiros) * 100)
            self.custo_op_total += pedido.distancia_total * melhor_carro.custo_op_km
            self.dist_s_pass += melhor_distancia
            self.emissao_CO2_total += pedido.distancia_total * melhor_carro.emissao_CO2

            melhor_carro.realizar_pedido(pedido)

            return True

        return False


    def guardar_estatisticas(self):
        with open(STATSFILENAME, "r") as file:
            content = json.load(file)

        tempo_total = 0
        for p in self.pedidos_resolvidos:
            tempo_total += p.tempo_resposta
        tempo_medio_resposta = tempo_total / len(self.pedidos_resolvidos)
        perc_media_lugares_vazios = sum(self.perc_lugares) / len(self.pedidos_resolvidos)
        data = {
            "algoritmo": self.tipo.value,
            "temp_med_resp": tempo_medio_resposta,
            "taxa_ocupacao": sum(self.taxa_ocupacao) / self.count_taxa_ocu,
            "custo_operacional": self.custo_op_total,
            "emissao_CO2": self.emissao_CO2_total,
            "nr_ped_rej": self.nr_ped_rej,
            "km_s_pass": self.dist_s_pass,
            "carros_bloq": len(self.veiculos_bloqueados),
            "perc_media_lugares": perc_media_lugares_vazios
        }

        content.append(data)

        with open(STATSFILENAME, "w") as file:
            json.dump(content, file)


    def registar_taxa_ocupacao(self):
        if self.instante_registo_taxa is None or self.instante_registo_taxa <= datetime.now():
            # determinar número de veiculos ocupados
            t = 0
            for v in self.veiculos:
                if not v.disponivel():
                    t += 1

            self.taxa_ocupacao.append((t / len(self.veiculos)) * 100)
            self.count_taxa_ocu += 1

            # registar taxa de ocupacao a cada 5 segundos
            self.instante_registo_taxa = datetime.now() + timedelta(seconds=5)


    def start(self):

        while self.nr_pedidos > 0 and self.veiculos:

            pedido = self.gestor_pedidos.proximo_pedido()

            if pedido is not None:
                if pedido.expirou():
                    pedido.estado = EstadoPedido.REJEITADO
                    self.nr_ped_rej += 1
                    self.nr_pedidos -= 1
                    print("[Taxi Green] pedido REJEITADO")
                elif not pedido.is_atrasado():
                    out = self.resolver_pedido(pedido)
                    print(f"[Taxi Green] pedido RECEBIDO:\n"
                          f" - Origem/Destino: {pedido.origem} -> {pedido.destino}\n"
                          f" - Horário: {pedido.horario_pretendido} segundos\n"
                          f" - Motorização: {pedido.motorizacao.value}\n"
                          f"-  Preferência: {pedido.preferencia.value}\n")

                    if out:
                        self.pedidos_resolvidos.append(pedido)
                        self.nr_pedidos -= 1
                        print(f"[Taxi Green] pedido RESOLVIDO:\n"
                              f" - Origem/Destino: {pedido.origem} -> {pedido.destino}\n"
                              f" - Distancia: {pedido.distancia_total} m\n"
                              f" - Tempo: {pedido.tempo_total:.2f} s\n")
                    else:
                        pedido.atrasar()
                        self.gestor_pedidos.repor_pedido(pedido)
            self.registar_taxa_ocupacao()

        self.nr_ped_rej += self.gestor_pedidos.nr_pedidos_atuais()

        self.guardar_estatisticas()
