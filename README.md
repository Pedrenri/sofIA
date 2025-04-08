# JarvisV3
JarvisV3 is a Streamlit-powered AI assistant inspired by Iron Man’s Jarvis. It offers both text and realtime audio interactions using OpenAI’s API, with customizable settings including dynamic voice selection and optional function calling.

## Features

- **Dual Interaction Modes:**  
  Text chat and realtime audio streaming.
- **Customizable Settings:**  
  Update API keys, model, prompt, voice, and function calling options via an in-app settings tab.
- **Dynamic Voice Selection:**  
  Choose from voices: alloy, ash, ballad, coral, echo, sage, shimmer, and verse.

## Prerequisites

- Python 3.7+
- An OpenAI API key

## Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/JarvisV3.git
   cd JarvisV3
   ```

2. **Create a Virtual Environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` File:**

   Create a file named `.env` in the root directory with the following content (replace placeholder values):

   ```ini
   OPENAI_API_KEY='your_api_key_here'
   OPENAI_MODEL='gpt-4o-mini-realtime-preview-2024-12-17'
   INITIAL_PROMPT='You are an assistant named Jarvis...'
   DEVICE='windows'
   VAD='True'
   FUNCTION_CALLING='False'
   VOICE='echo'
   INCLUDE_TIME='True'
   INCLUDE_DATE='True'
   ```

## Running the App

Start the Streamlit app with:

```bash
streamlit run app.py
```

Open the displayed URL in your browser to interact with JarvisV3.

## License

This project is licensed under the MIT License. Feel free to contribute!

Enjoy using JarvisV3!
