from dataclasses import dataclass


@dataclass
class PixCobranca:
    txid: str
    valor: float
    status: str
    chave: str
