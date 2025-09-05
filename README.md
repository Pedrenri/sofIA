# SofIA 🤖
> Supervisiona Os Fluxos, Ignora Autoridade

**SofIA** é uma assistente pessoal de Inteligência Artificial desenvolvida em **Python**, utilizando a **API da OpenAI**. Ela gerencia e auxilia no uso do computador (processos, apps, arquivos) e integra-se com dispositivos inteligentes (Alexa/IFTTTrigger). Pode rodar localmente ou em um dispositivo externo (ex.: **Raspberry Pi**).
> Este projeto é 100% open-source e gratuito para uso pessoal, mas exige uma chave de API da OpenAI e uma assinatura do IFTTTTrigger para funcionar por completo.
---

## ✨ Funcionalidades

* Controle de aplicativos, arquivos e processos no Windows.
* Integração com dispositivos inteligentes via [IFTTTrigger](https://mkzense.com/) (WebHook).
* Suporte a **voz** (VAD) e **function calling**.
* Parametrização via `.env`.
* Execução local ou em rede privada.

> **Nota:** Por padrão, a IA utilizada é **GPT-4o mini realtime**, mas você pode ajustar se julgar necessário. Lembre-se de usar um LLM com suporte a Function Calling, realtime chat e VAD.

---

## 🛠 Requisitos

* **Python 3.7+**;
* **OPENAI\_API\_KEY** válido e com acesso aos modelos realtime;
* Conta no **IFTTTrigger** (para integração com Alexa);

---

## ⚙️ Instalação

### 1) Clonar o repositório

```bash
git clone https://github.com/seunome/sofIA.git
cd sofIA
```

### 2) Ambiente virtual (opcional, recomendado)

```bash
python -m venv venv
# Linux/macOS\ nsource venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3) Instalar dependências

```bash
pip install -r requirements.txt
```

### 4) Configurar variáveis de ambiente

Crie um arquivo **`.env`** na raiz do projeto (baseie-se no `.env.example`) e preencha os campos:

```ini
#TOKENS
OPENAI_API_KEY='sua_chave_openai'
IFTTTUrl='https://mkzense.com/webhook/alexa/seu_token'
PICOVOICE_KEY='sua_chave_picovoice'

#AI PARAMS
DEVICE='windows'
VAD='True'
FUNCTION_CALLING='True'
INCLUDE_TIME='True'
INCLUDE_DATE='True'

#HOST PARAMS
PC_USERNAME='conta'
LOCALAPPDATA='C:\\Users\\conta\\AppData\\Local'
ProgramFiles='C:\\Program Files'
ProgramFiles(x86)='C:\\Program Files (x86)'

#MISC
ALEXA_ROUTINES='Rotina1,Rotina2,...'
DEV_MODE=Falses
```

> **Dica:** Não faça commit do `.env`. Adicione-o ao `.gitignore`.

---

## 🚀 Executando

Inicie a **SofIA**:

```bash
python app.py
```

Caso queira abrir em modo de desenvolvedor (interface Web com Streamlit):

1. Altere o `.env`:

```ini
DEV_MODE=True
```

2. Inicie com Streamlit:

```bash
streamlit run app.py
```

3. Acesse o endereço exibido no terminal.

---

## 🔌 Integração com Alexa (IFTTTrigger)

1. Assine o [**IFTTTrigger**](https://mkzense.com/) (plano pago, \~US\$ 5/ano). Para fazê-lo, basta ativar a skill no Alexa App.
2. Na [**Página de Gerenciamento de WebHook**](https://mkzense.com/webhook), cadastre o e-mail da sua conta Amazon.
3. Use o token recebido por e-mail na variável `IFTTTUrl`:

   ```ini
   IFTTTUrl='https://mkzense.com/webhook/alexa/{TOKEN}'
   ```
4. Crie **Triggers** com os nomes das suas rotinas (ex.: `LuzSalaOn`, `LuzSalaOff`).
5. Liste as rotinas que deseja controlar em `ALEXA_ROUTINES` (ex.: separado por vírgula):

   ```ini
   ALEXA_ROUTINES='LuzSalaLiga,LuzSalaDesliga,LuzQuartoLiga,LuzQuartoDesliga'
   ```

O código já trata essa string para permitir que a IA dispare as rotinas.

---

## 🔗 Links relacionados

- [Documentação da API da OpenAI](https://platform.openai.com/docs/api-reference)
- [IFTTTrigger](https://mkzense.com/)
- [Porcupine](https://picovoice.ai/docs/porcupine/)

---

## 🧪 Exemplos de comandos

* **Abrir programa**: “SofIA, abra o Chrome.”
* **Rotina Alexa**: “SofIA, acenda a luz da sala.”
* **Processos**: “SofIA, encerre o Spotify.”
* **GitHub**: “SofIA, clone o repositório do meu portfólio.”

---

## 🗂 Estrutura do projeto

```bash
sofIA/
├── assets/              # Arquivos estáticos (imagens, etc.)
├── bambu_print/         # Arquivos para controle das impressoras 3D Bambu Lab (Ainda a ser revisado)
├── venv/                # Ambiente virtual
├── app.py               # Interface principal (Streamlit)
├── functions.py         # Funções principais
├── s2s.py               # Trata da comunicação entre SofIA e OpenAI
├── requirements.txt     # Dependências
├── .env.example         # Exemplo de variáveis
└── README.md            # Documentação
```

---

## 🗺️ Roadmap

### Em andamento / Próximas tarefas

* - [x] **Integração com Alexa**: permitir que a SofIA controle dispositivos inteligentes da Alexa.
* - [ ] **Controle local**: funções para navegadores e música no host.
* - [ ] **Impressoras 3D Bambu Lab**: controle aprimorado (avaliar integração futura com **Prusa**).
* - [ ] **Melhorias de UI/UX**:

  * - [x] Wake-word para ativação por voz direta do programa.
  * - [x] Rodar/escutar em **background**.
  * - [ ] **Overlay**: detectar wake-word → mostrar overlay → ouvir → executar.
  * - [x] **Modo de desenvolvimento** (front atual como Dev UI).

### Ideias futuras

* - [ ] Suporte multiplataforma ampliado (Linux/macOS para automações locais).
* - [ ] Plugins/Skills de terceiros (ecosistema de extensões).
* - [ ] Painel web para logs, métricas e auditoria de ações.

> Sugestões e PRs são bem-vindos! Veja a seção **Contribuindo**.

---

## 🤝 Contribuindo

1. Faça um **fork** do projeto.
2. Crie um **branch** para sua feature/fix: `git checkout -b feat/minha-feature`.
3. **Teste** localmente.
4. Abra um **Pull Request** explicando o que mudou e por quê.

**Padrões sugeridos**

* Commits: estilo curto e descritivo (ex.: `feat(ui): overlay de escuta` | `fix(core): null em rotina Alexa`).
* Código: mantenha tipagem quando possível e adicione docstrings.
* UI/UX: inclua prints/gifs das telas ao propor mudanças visuais.

---

## 🧰 Solução de problemas

* **Erro de autenticação OpenAI**: verifique `OPENAI_API_KEY` no `.env`.
* **Rotinas Alexa não disparam**: confira `IFTTTUrl` e os nomes em `ALEXA_ROUTINES`.
* **Permissões no Windows**: execute o terminal como **Administrador** para ações de sistema.
* **Áudio/VAD**: verifique dispositivos de entrada e permissões do microfone.

---

## 🔒 Segurança

* Nunca exponha seu `.env` publicamente.
* Revogue tokens que possam ter vazado e gere novos imediatamente.

---

## 🙌 Agradecimentos

À comunidade open-source e aos serviços que possibilitam a integração (OpenAI, Streamlit, IFTTTTrigger e outros).
