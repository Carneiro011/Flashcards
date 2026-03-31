# app/services/text_processor.py

import re
import random
from typing import List
from app.models.flashcard import Flashcard, TipoFlashcard


class TextProcessor:
    """
    Processa texto por meio de regras linguísticas simples.
    
    ESTRATÉGIA GERAL:
    1. Dividir o texto em sentenças
    2. Para cada sentença, extrair o "conceito principal"
    3. Aplicar templates de flashcard conforme o tipo sorteado
    4. Limitar em 5 flashcards (conforme RF02)
    
    LIMITAÇÕES desta abordagem:
    - Não entende semântica (significado)
    - Pode gerar perguntas gramaticalmente estranhas
    - Ideal para demonstração e MVP
    """

    # Templates definem os padrões de cada tipo de flashcard
    TEMPLATES = {
        TipoFlashcard.VERDADEIRO_FALSO: [
            "É correto afirmar que: {sentenca}?",
            "A seguinte afirmação é verdadeira: {sentenca}?",
        ],
        TipoFlashcard.PERGUNTA_RESPOSTA: [
            "O que você sabe sobre {conceito}?",
            "Explique com suas palavras: {conceito}.",
            "Como {conceito} se relaciona com o tema estudado?",
        ],
        TipoFlashcard.PREENCHA_LACUNA: [
            # A lacuna será criada substituindo o conceito por "______"
        ],
    }

    def extrair_sentencas(self, texto: str) -> List[str]:
        """
        Divide o texto em sentenças usando pontuação como delimitador.
        
        Regex explicado:
        - [.!?]    → qualquer ponto final, exclamação ou interrogação
        - \s+      → seguido de um ou mais espaços
        - (?=[A-Z])→ lookahead: próximo caractere é maiúscula (início de frase)
        
        Exemplo:
            "Mitocôndria é a usina da célula. Ela produz ATP."
            → ["Mitocôndria é a usina da célula", "Ela produz ATP"]
        """
        sentencas = re.split(r'[.!?]\s+(?=[A-Z])', texto.strip())
        # Remove sentenças muito curtas (menos de 5 palavras) — pouco informativas
        return [s.strip() for s in sentencas if len(s.split()) >= 5]

    def extrair_conceito(self, sentenca: str) -> str:
        """
        Extrai o conceito principal de uma sentença.
        
        HEURÍSTICA SIMPLES:
        O sujeito de uma frase em português tende a estar no início.
        Pegamos as primeiras 1 a 3 palavras como "conceito".
        
        Palavras vazias (stopwords) são ignoradas.
        
        Exemplo:
            "A fotossíntese converte luz em energia"
            → "fotossíntese" (ignora artigo "A")
        """
        stopwords = {
            'a', 'o', 'as', 'os', 'um', 'uma', 'uns', 'umas',
            'de', 'da', 'do', 'das', 'dos', 'em', 'no', 'na',
            'e', 'é', 'são', 'foi', 'ser', 'estar', 'que', 'se'
        }
        palavras = sentenca.split()
        conceito_palavras = []

        for palavra in palavras[:5]:  # Analisa as primeiras 5 palavras
            palavra_limpa = re.sub(r'[^\w]', '', palavra.lower())
            if palavra_limpa not in stopwords and len(palavra_limpa) > 2:
                conceito_palavras.append(palavra)
            if len(conceito_palavras) == 2:  # Pega no máximo 2 palavras
                break

        return ' '.join(conceito_palavras) if conceito_palavras else palavras[0]

    def criar_lacuna(self, sentenca: str, conceito: str) -> tuple[str, str]:
        """
        Cria o flashcard de preencha a lacuna.
        
        Substitui o conceito por "______" na sentença.
        Retorna a frente (com lacuna) e o verso (resposta).
        
        Exemplo:
            sentenca = "A mitocôndria produz energia para a célula"
            conceito = "mitocôndria"
            → frente: "A ______ produz energia para a célula"
            → verso:  "mitocôndria"
        """
        # re.sub com re.IGNORECASE para pegar variações de capitalização
        frente = re.sub(
            re.escape(conceito),
            "______",
            sentenca,
            count=1,           # Substitui apenas a primeira ocorrência
            flags=re.IGNORECASE
        )
        return frente, conceito

    def gerar_flashcards(self, texto: str, max_cards: int = 5) -> List[Flashcard]:
        """
        Função principal: recebe texto e retorna lista de Flashcards.
        
        Algoritmo:
        1. Extrai sentenças do texto
        2. Embaralha para variedade
        3. Para cada sentença, sorteia um tipo de flashcard
        4. Cria o flashcard com o template adequado
        5. Para ao atingir max_cards
        
        Args:
            texto:     Texto inserido pelo usuário
            max_cards: Número máximo de flashcards (padrão 5, conforme RF02)
            
        Returns:
            Lista de objetos Flashcard
        """
        sentencas = self.extrair_sentencas(texto)

        if not sentencas:
            raise ValueError("O texto fornecido é muito curto ou não contém sentenças completas.")

        # Embaralha para não pegar sempre as primeiras sentenças
        random.shuffle(sentencas)

        flashcards = []
        tipos = list(TipoFlashcard)  # [VERDADEIRO_FALSO, PREENCHA_LACUNA, PERGUNTA_RESPOSTA]

        for i, sentenca in enumerate(sentencas[:max_cards]):
            # Cicla pelos tipos para garantir variedade (RF03)
            tipo = tipos[i % len(tipos)]
            conceito = self.extrair_conceito(sentenca)

            if tipo == TipoFlashcard.VERDADEIRO_FALSO:
                template = random.choice(self.TEMPLATES[TipoFlashcard.VERDADEIRO_FALSO])
                frente = template.format(sentenca=sentenca)
                verso = "Verdadeiro — esta afirmação está correta conforme o texto."
                dica = f"Relembre o contexto sobre: {conceito}"

            elif tipo == TipoFlashcard.PREENCHA_LACUNA:
                frente, verso = self.criar_lacuna(sentenca, conceito)
                dica = f"A palavra tem {len(conceito)} caracteres."

            else:  # PERGUNTA_RESPOSTA
                template = random.choice(self.TEMPLATES[TipoFlashcard.PERGUNTA_RESPOSTA])
                frente = template.format(conceito=conceito)
                verso = sentenca  # A própria sentença é a resposta-base
                dica = "Compare sua resposta com o texto original."

            flashcard = Flashcard(
                tipo=tipo,
                frente=frente,
                verso=verso,
                conceito=conceito,
                dica=dica
            )
            flashcards.append(flashcard)

        return flashcards