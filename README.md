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
   OPENAI_API_KEY='sua_chave'
   OPENAI_MODEL='gpt-4o-mini-realtime-preview-2024-12-17'
   INITIAL_PROMPT='Você é um assistente virtual chamado SofIA. Sua função é gerenciar e controlar meu computador e alguns itens inteligentes que tenho aqui na minha casa. Seu criador se chama Pedro Henri, e é ele que te atualiza. O nome de usuário que você sempre vai usar para criar e manipular arquivos é "conta", e você nunca pode trocar isso. Caso seja pedido para criar código, não use nada de formatação LaTEX ou coisa assim ("\\", por exemplo), pois isso vai quebrar o código. Remova também as aspas geradas. Mantenha suas respostas sempre o mais curtas possível, não passando de 5 palavras para afirmar que você cumpriu uma solicitação, por exemplo.'
   DEVICE='windows'
   VAD='True'
   FUNCTION_CALLING='True'
   VOICE='sage'
   INCLUDE_TIME='True'
   INCLUDE_DATE='True'
   PC_USERNAME='conta'
   LOCALAPPDATA='C:\\Users\\conta\\AppData\\Local'
   ProgramFiles='C:\\Program Files'
   ProgramFiles(x86)='C:\\Program Files (x86)'
   GITHUB_TOKEN='seu_token'
   ```

## Rodando o App

Rode o app streamlit com:

```bash
streamlit run app.py
```

Abra o URL mostrado no seu navegador.

Faça bom uso!
