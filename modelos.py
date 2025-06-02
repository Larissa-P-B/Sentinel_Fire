#Nome: Larissa Pereira Biusse
#RM: 564068

from dataclasses import dataclass, field
import random
from typing import List

@dataclass
class ContatoEmergencia:
    """Contatos para notificação de emergências"""
    nome: str
    email: str
    telefone: str
    tipo: str  # "autoridade" ou "comunidade"
    regioes: List[str]  # Regiões que este contato monitora


@dataclass(order=True)
class Ocorrencia:
    """Classe que representa uma ocorrência de incêndio"""
    prioridade: int
    local: list
    severidade: int
    regiao: str
    id: int = field(default_factory=lambda: random.randint(1000, 9999))
    status: str = field(default="Pendente")
    fogo_confirmado: bool = field(default=False)
    fogo_apagado: bool = field(default=False)
    tempo_inicio_fogo: float = field(default=0.0)
    tempo_fim_fogo: float = field(default=0.0)

    def __post_init__(self):
        """Configura prioridade baseada na severidade e região"""
        if not isinstance(self.local, (list, tuple)) or len(self.local) != 2:
            raise ValueError("Local deve ser uma lista/tupla com [latitude, longitude]")

        self.prioridade = -self.severidade  # Heap máximo
        if self.regiao in ["Amazônia", "Pantanal"]:
            self.prioridade *= 2  # Prioridade dobrada para regiões críticas








