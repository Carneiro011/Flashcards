# run.py

from app import create_app

app = create_app("development")

if __name__ == "__main__":
    # debug=True: recarrega automaticamente ao salvar arquivos
    # NÃO use debug=True em produção
    app.run(debug=True, port=5000)