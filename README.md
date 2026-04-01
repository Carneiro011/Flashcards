# 🧠 Flashcard Generator (Flask + IA)

Aplicação web para geração automática de flashcards a partir de textos, utilizando **IA (Google Gemini)** ou **regras NLP locais** como fallback.

---

## 🚀 Funcionalidades

* Geração automática de flashcards a partir de texto
* Dois modos:

  * 🤖 **IA (Gemini)** — mais inteligente e contextual
  * 🧠 **Regras locais (NLP)** — funciona sem internet/API
* 6 flashcards por execução:

  * 2 Verdadeiro/Falso
  * 2 Preencha a lacuna
  * 2 Pergunta/Resposta
* Fallback automático caso a IA falhe

---

## 🏗️ Estrutura do Projeto

```
app/
├── controllers/        # Rotas Flask
├── services/           # Lógica (IA e NLP)
├── models/             # Estrutura dos dados
├── static/             # CSS / JS
├── templates/          # HTML
run.py                  # Inicialização do app
.env                    # Variáveis de ambiente
```

---

## ⚙️ Instalação

```bash
git clone <repo>
cd project
python -m venv venv
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

---

## 🔑 Configuração

Crie um arquivo `.env` na raiz:

```
USE_AI=true
GEMINI_API_KEY=sua_chave_aqui
```

---

## ▶️ Executando

```bash
python run.py
```

Acesse:

```
http://127.0.0.1:5000
```

---

## 🔄 API

### Gerar flashcards

```http
POST /api/gerar
```

**Body:**

```json
{
  "texto": "Seu texto aqui...",
  "usar_ia": true
}
```

---

## 🧠 Tecnologias

* Flask
* Python
* Google Gemini (google-genai)
* Regex / NLP simples

---

## ⚠️ Observações

* A IA pode falhar dependendo da chave/modelo → fallback automático é usado
* O modo sem IA utiliza heurísticas simples (não semântico)

---

## 📌 Próximos passos

* Modo múltipla escolha (estilo ENEM)
* Persistência em banco de dados
* Interface com flip cards
* Sistema de pontuação

---

## 👨‍💻 Autor

Guilherme Carneiro
