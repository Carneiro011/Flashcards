# config.py

import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do arquivo .env

class Config:
    """Configuração base — compartilhada por todos os ambientes."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-inseguro-troque-em-producao")
    USE_AI     = os.getenv("USE_AI", "false").lower() == "true"
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class DevelopmentConfig(Config):
    """Configuração de desenvolvimento — mais verbosa."""
    DEBUG = True

class ProductionConfig(Config):
    """Configuração de produção — segura e otimizada."""
    DEBUG = False

# Mapa para seleção via variável de ambiente
config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}