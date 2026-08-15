
from datetime import datetime, timedelta


class Localizacao:

    def __init__(
        self,
        nome: str,
        posto_recarga: bool,
        bomba_combustivel: bool,
        numero_lugares: int,
        posicao : tuple
    ):
        self.nome = nome
        self.posto_recarga = posto_recarga
        self.bomba_combustivel = bomba_combustivel
        self.numero_lugares = numero_lugares
        self.posicao = posicao
        self.instantes = []
        for i in range(0, self.numero_lugares):
            self.instantes.append(None)

    def tem_lugar_disponivel(self) -> bool:
        for i in self.instantes:
            if i is None or i < datetime.now():
                return True
        return False

    def ocupar_lugar(self, tempo : int):
        for i in self.instantes:
            if i is None or i < datetime.now():
                i = datetime.now() + timedelta(seconds=tempo)
                break

    def __str__(self) -> str:
        return (
            f"Localização {self.nome}:\n"
            f"\tRecarga elétrica: {'sim' if self.posto_recarga else 'não'}\n"
            f"\tCombustível: {'sim' if self.bomba_combustivel else 'não'}\n"
            f"\tLugares: {self.numero_lugares}\n"
            f"\tPosição: {self.posicao}"
        )
