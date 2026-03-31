# app/controllers/flashcard_controller.py

from flask import Blueprint, request, jsonify, render_template, current_app
from app.services.text_processor import TextProcessor
from app.services.ai_service import AIFlashcardService

# Blueprint agrupa rotas relacionadas — equivalente a um "módulo de rotas"
# url_prefix="/api" faz todas as rotas começarem com /api
flashcard_bp = Blueprint("flashcard", __name__, url_prefix="")


@flashcard_bp.route("/", methods=["GET"])
def index():
    """
    Rota raiz: serve a página principal (a View do MVC).
    
    GET / → retorna index.html
    """
    return render_template("index.html")


@flashcard_bp.route("/api/gerar", methods=["POST"])
def gerar_flashcards():
    """
    Endpoint principal da API.
    
    Recebe: POST /api/gerar
    Body: { "texto": "...", "usar_ia": false }
    
    Retorna: 
        200: { "flashcards": [...], "total": 5, "modo": "regras" }
        400: { "erro": "mensagem de erro" }
        500: { "erro": "erro interno" }
    
    Responsabilidades do Controller:
    ✓ Receber e validar entrada
    ✓ Delegar processamento ao Service
    ✓ Serializar e retornar resposta
    ✗ NÃO deve conter lógica de negócio
    """
    # 1. RECEBER E VALIDAR ENTRADA
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Corpo da requisição deve ser JSON"}), 400

    texto = dados.get("texto", "").strip()
    usar_ia = dados.get("usar_ia", False)

    if not texto:
        return jsonify({"erro": "O campo 'texto' é obrigatório"}), 400

    if len(texto) < 50:
        return jsonify({
            "erro": "Texto muito curto. Insira pelo menos 50 caracteres para gerar flashcards relevantes."
        }), 400

    if len(texto) > 5000:
        return jsonify({
            "erro": "Texto muito longo. Limite de 5000 caracteres."
        }), 400

    # 2. DELEGAR AO SERVICE CORRETO
    try:
        if usar_ia and current_app.config.get("USE_AI"):
            # Modo IA: usa Google Gemini
            service = AIFlashcardService()
            flashcards = service.gerar_flashcards(texto)
            modo = "ia"
        else:
            # Modo regras: processamento local
            processor = TextProcessor()
            flashcards = processor.gerar_flashcards(texto)
            modo = "regras"

    except ValueError as e:
        # Erro de validação ou processamento esperado
        return jsonify({"erro": str(e)}), 400

    except Exception as e:
        # Erro inesperado — loga internamente, não expõe detalhes ao usuário
        current_app.logger.error(f"Erro ao gerar flashcards: {e}")
        return jsonify({"erro": "Erro interno ao processar o texto. Tente novamente."}), 500

    # 3. SERIALIZAR E RETORNAR
    return jsonify({
        "flashcards": [fc.to_dict() for fc in flashcards],
        "total":      len(flashcards),
        "modo":       modo,
    }), 200