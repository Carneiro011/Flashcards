# app/services/ai_service.py

import os
import json
import google.generativeai as genai
from typing import List
from app.models.flashcard import Flashcard, TipoFlashcard


class AIFlashcardService:
    """
    Gera flashcards usando o Google Gemini API.
    
    Por que Gemini e não OpenAI?
    - Tem tier gratuito generoso (ideal para estudantes)
    - Gemini 1.5 Flash é rápido e eficiente para tarefas de texto
    - API em Python é simples e bem documentada
    
    Configuração necessária:
    1. Criar conta em aistudio.google.com
    2. Gerar uma API Key
    3. Adicionar ao arquivo .env: GEMINI_API_KEY=sua_chave_aqui
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY não encontrada. "
                "Adicione ao arquivo .env: GEMINI_API_KEY=sua_chave"
            )
        genai.configure(api_key=api_key)
        # Usamos Flash: mais rápido e gratuito, ideal para MVP
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def _montar_prompt(self, texto: str) -> str:
        """
        Engenharia de prompt: instrução precisa para o modelo.
        
        Boas práticas de prompt engineering:
        1. Papel claro ("Você é um professor...")
        2. Tarefa específica (gerar exatamente 5 flashcards)
        3. Formato de saída definido (JSON)
        4. Exemplos inline (few-shot)
        5. Restrição de formato (APENAS JSON)
        """
        return f"""
Você é um professor universitário especialista em criar materiais de estudo.

Sua tarefa: analisar o texto abaixo e gerar EXATAMENTE 5 flashcards educativos.

REGRAS OBRIGATÓRIAS:
1. Gere flashcards dos 3 tipos: verdadeiro_falso, preencha_lacuna, pergunta_resposta
2. Baseie TODOS os flashcards no conteúdo do texto fornecido
3. Retorne APENAS JSON válido, sem texto antes ou depois
4. Siga EXATAMENTE o schema abaixo

SCHEMA JSON:
{{
  "flashcards": [
    {{
      "tipo": "verdadeiro_falso" | "preencha_lacuna" | "pergunta_resposta",
      "frente": "texto da pergunta/afirmação/lacuna",
      "verso": "resposta correta",
      "conceito": "conceito principal abordado",
      "dica": "dica de estudo (1 frase)"
    }}
  ]
}}

TEXTO PARA ANÁLISE:
{texto}

Lembre-se: retorne SOMENTE o JSON. Nada mais.
"""

    def gerar_flashcards(self, texto: str) -> List[Flashcard]:
        """
        Chama a API do Gemini e converte a resposta em objetos Flashcard.
        
        Fluxo:
        1. Monta o prompt com o texto do usuário
        2. Envia para a API
        3. Faz parse do JSON retornado
        4. Converte cada item em objeto Flashcard
        5. Retorna a lista
        
        Tratamento de erros:
        - json.JSONDecodeError: modelo retornou algo que não é JSON válido
        - KeyError: JSON válido mas sem os campos esperados
        """
        prompt = self._montar_prompt(texto)

        # Chamada à API — esta linha é assíncrona internamente no Gemini
        response = self.model.generate_content(prompt)

        # O modelo às vezes envolve JSON em ```json ... ```
        # Este bloco limpa isso antes do parse
        texto_resposta = response.text.strip()
        if texto_resposta.startswith("```"):
            # Remove delimitadores de código markdown
            linhas = texto_resposta.split('\n')
            texto_resposta = '\n'.join(linhas[1:-1])

        try:
            dados = json.loads(texto_resposta)
        except json.JSONDecodeError as e:
            raise ValueError(f"A IA retornou formato inválido: {e}\nResposta: {texto_resposta[:200]}")

        flashcards = []
        for item in dados.get("flashcards", []):
            flashcard = Flashcard(
                tipo=TipoFlashcard(item["tipo"]),   # Enum valida o valor
                frente=item["frente"],
                verso=item["verso"],
                conceito=item["conceito"],
                dica=item.get("dica"),              # .get() = None se ausente
            )
            flashcards.append(flashcard)

        return flashcards