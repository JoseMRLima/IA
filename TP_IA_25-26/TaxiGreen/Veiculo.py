
from datetime import datetime, timedelta

from Pedido import Pedido, TipoMotorizacao

class Veiculo:
    """Representa um veículo da frota"""

    def __init__(
        self,
        matricula: str,
        marca: str,
        modelo: str,
        motorizacao: TipoMotorizacao,
        autonomia_maxima: int,
        nr_passageiros: int,
        custo_op_km: float,
        tempo_abastecer : int,
        localizacao : str,
        emissao_CO2 : float
    ):
        self.matricula = matricula
        self.marca = marca
        self.modelo = modelo
        self.motorizacao = motorizacao
        self.autonomia_maxima = autonomia_maxima
        self.autonomia_atual = autonomia_maxima
        self.nr_passageiros = nr_passageiros
        self.custo_op_km = custo_op_km
        self.tempo_abastecer = tempo_abastecer
        self.localizacao = localizacao
        self.instante = None
        self.emissao_CO2 = emissao_CO2

    def disponivel(self) -> bool:
        return self.instante is None or self.instante <= datetime.now()

    def precisa_abastecer(self) -> bool:
        return (self.autonomia_atual / self.autonomia_maxima) < 0.9

    def pode_fazer_viagem(self, distancia : int) -> bool:
        if self.autonomia_atual > distancia:
            t = self.autonomia_atual - distancia
            return (t / self.autonomia_maxima) > 0.10
        return False

    def realizar_pedido(self, pedido : Pedido):
        self.instante = datetime.now() + timedelta(seconds=pedido.tempo_total)
        self.autonomia_atual -= pedido.distancia_total
        self.localizacao = pedido.destino

    def abastecer(self, posto : str, tempo : int):
        self.instante = datetime.now() + timedelta(seconds=(self.tempo_abastecer + tempo))
        self.localizacao = posto
        self.autonomia_atual = self.autonomia_maxima
        print(f"{self.matricula} a abastecer em {posto}")

    def __str__(self) -> str:
        return (
            f"Veículo {self.matricula}\n"
            f"  Marca/Modelo: {self.marca} {self.modelo}\n"
            f"  Motorização: {self.motorizacao.value}\n"
            f"  Autonomia: {self.autonomia_atual} / {self.autonomia_maxima} km\n"
            f"  Capacidade: {self.nr_passageiros} passageiros\n"
            f"  Custo operacional: {self.custo_op_km:.2f} €/km\n"
            f"  Tempo abastecimento: {self.tempo_abastecer} segundos\n"
            f"  Localização: {self.localizacao}"
        )
