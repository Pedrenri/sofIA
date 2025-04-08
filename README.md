# sofIA
SofIA é uma assistente pessoal de IA criada usando Python que utiliza a API da OpenAI e consegue gerenciar e auxiliar no uso do computador.

## Requisitos

- Python 3.7+
- Chave de API da OpenAI

## Setup

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/seunome/sofIA.git
   cd sofIA
   ```

2. **Crie um ambiente virtual (opcional, mas recomendado):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Instale as Dependências:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Crie o seu `.env`:**

   Crie um arquivo chamado `.env` no diretório raiz com (troque os valores de placeholder):

   ```ini
   OPENAI_API_KEY='your_api_key_here'
   OPENAI_MODEL='gpt-4o-mini-realtime-preview-2024-12-17'
   INITIAL_PROMPT='Você é uma assistente pessoal chamada sofIA...'
   DEVICE='windows'
   VAD='True'
   FUNCTION_CALLING='False'
   VOICE='echo'
   INCLUDE_TIME='True'
   INCLUDE_DATE='True'
   ```

## Rodando o App

Rode o app streamlit com:

```bash
streamlit run app.py
```

Abra o URL mostrado no seu navegador.


Faça bom uso!
