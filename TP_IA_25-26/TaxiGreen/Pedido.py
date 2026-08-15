
from enum import Enum
from datetime import datetime, timedelta


class Preferencia(Enum):
    LOW_COST = "low cost"
    FAST = "rapido"


class TipoMotorizacao(Enum):
    """Tipo de motorização do veículo."""
    ELETRICO = "elétrico"
    COMBUSTAO = "combustão"


class EstadoPedido(Enum):
    REJEITADO = "rejeitado"
    EM_ESPERA = "em espera"
    REALIZADO = "realizado"
    INVALIDO = "inválido"


class PrioridadePedido(Enum):
    NORMAL = "normal"
    URGENTE = "urgente"


class Pedido:

    def __init__(
        self,
        origem,
        destino,
        numero_passageiros: int,
        horario_pretendido: int,
        prioridade: PrioridadePedido,
        motorizacao: TipoMotorizacao,
        preferencia: Preferencia
    ):
        self.origem = origem
        self.destino = destino
        self.numero_passageiros = numero_passageiros
        # número máximo de segundos que o cliente espera
        self.horario_pretendido = horario_pretendido
        self.prioridade = prioridade
        self.motorizacao = motorizacao
        self.preferencia = preferencia
        # instante que o pedido foi criado
        self.instante_criacao = datetime.now()
        self.instante_atraso = None
        self.estado = EstadoPedido.EM_ESPERA
        self.tempo_resposta = 0
        self.tempo_total = 0
        self.distancia_total = 0

    def expirou(self) -> bool:
        return self.instante_criacao + timedelta(seconds=self.horario_pretendido) < datetime.now()

    def atrasar(self):
        # atrasar 5 segundos
        self.instante_atraso = datetime.now() + timedelta(seconds=5)

    def is_atrasado(self):
        return self.instante_atraso is not None and self.instante_atraso > datetime.now()

    def __str__(self) -> str:
        return (
            f"Pedido de Transporte\n"
            f"  Origem/Destino: {self.origem} -> {self.destino}\n"
            f"  Passageiros: {self.numero_passageiros}\n"
            f"  Espera Máxima: {self.horario_pretendido} segundos\n"
            f"  Prioridade: {self.prioridade.value}\n"
            f"  Tipo de motorização: {self.motorizacao.value}"
        )
