# app/models/flashcard.py

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid

class TipoFlashcard(Enum):
    """
    Enum garante que só tipos válidos sejam usados.
    Evita strings mágicas como "vf", "verd", "v/f" espalhadas pelo código.
    """
    VERDADEIRO_FALSO   = "verdadeiro_falso"
    PREENCHA_LACUNA    = "preencha_lacuna"
    PERGUNTA_RESPOSTA  = "pergunta_resposta"


@dataclass
class Flashcard:
    """
    Representa um flashcard gerado pelo sistema.
    
    @dataclass é um decorador do Python que automaticamente gera
    __init__, __repr__ e __eq__ baseados nos campos declarados.
    Isso evita código boilerplate desnecessário.
    
    Atributos:
        id          - Identificador único (UUID)
        tipo        - Tipo do flashcard (TipoFlashcard)
        frente      - Texto exibido na frente do cartão (pergunta/afirmação)
        verso       - Texto exibido no verso (resposta)
        conceito    - Conceito-chave que originou o flashcard
        dica        - Dica opcional para ajudar o estudante
    """
    tipo:     TipoFlashcard
    frente:   str
    verso:    str
    conceito: str
    id:       str            = field(default_factory=lambda: str(uuid.uuid4()))
    dica:     Optional[str]  = None

    def to_dict(self) -> dict:
        """
        Serializa o flashcard para dicionário Python.
        Necessário para converter para JSON na resposta da API.
        
        Retorna:
            dict com todos os campos do flashcard
        """
        return {
            "id":       self.id,
            "tipo":     self.tipo.value,   # .value pega a string do Enum
            "frente":   self.frente,
            "verso":    self.verso,
            "conceito": self.conceito,
            "dica":     self.dica,
        }