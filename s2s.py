import os
from dotenv import load_dotenv
import json
import base64
import threading
import websocket
import pyaudio
import datetime
import subprocess
import time
import queue
from functions import lights_control, run_os_command, print_message, print_stl, create_file, open_application

load_dotenv()  # carrega o .env

alexa_routines = os.getenv("ALEXA_ROUTINES", "").split(",")

class SofIAClient:
    def __init__(self, *, api_key=None, device=None, 
                 include_date=True, include_time=True, mode="realtime", function_calling=True):
        """
        mode: "realtime" for audio chat (with mic streaming) or "text" for text-only chat.
        function_calling: Enable or disable function calling.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found in .env file.")
        self.device = device or os.getenv("DEVICE", "unknown")
        self.model = "gpt-4o-mini-realtime-preview-2024-12-17"
        self.include_date = include_date
        self.include_time = include_time
        self.mode = mode
        self.function_calling = function_calling
        self.pc_username = os.getenv("PC_USERNAME", "YourUsername")
        self.last_audio_event = 0
        self.ws = None
        self.ws_thread = None
        self.running = False
        
        self.p = pyaudio.PyAudio()
        self.output_stream = None
        self.mute_mic = False

        self.on_text_response = None

    def append_tools_to_message(self, message: str) -> str:
        now = datetime.datetime.now()
        additions = []
        if self.include_date:
            additions.append(f"Date: {now.strftime('%Y-%m-%d')}")
        if self.include_time:
            additions.append(f"Time: {now.strftime('%H:%M:%S')}")
        if additions:
            return f"{message} ({' | '.join(additions)})"
        else:
            return message

    def send_text_message(self, message: str, role: str = "user"):

        print(f"DEBUG: Enviando mensagem: {message}")
        modalities = ["text", "audio"] if self.mode == "realtime" else ["text"]

        full_text = self.append_tools_to_message(message)
        conversation_event = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": role,
                "content": [
                    {"type": "input_text", "text": full_text}
                ]
            }
        }
        # print(f"DEBUG: Enviando mensagem: {full_text}")
        self.ws.send(json.dumps(conversation_event))
        response_create_event = {
            "type": "response.create",
            "response": {
                "modalities": modalities
            }
        }
        self.ws.send(json.dumps(response_create_event))

    def ask_sync(self, message: str, timeout=30) -> str:
        """
        Synchronously send a text message and wait until a response is received.
        Returns the response text or a timeout message.
        """
        response_queue = queue.Queue()
        original_callback = self.on_text_response

        def temp_callback(text):
            response_queue.put(text)

        self.on_text_response = temp_callback
        self.send_text_message(message)
        try:
            answer = response_queue.get(timeout=timeout)
        except queue.Empty:
            answer = "No response received within timeout."
        self.on_text_response = original_callback
        return answer

    

    def on_message(self, ws, message):
        event = json.loads(message)
        event_type = event.get("type")
        # Descomenta os prints que precisar
        # print(f"DEBUG: Recebido evento tipo: {event_type}")
        
        if event_type == "response.audio.delta":

            if not self.mute_mic:
                self.mute_mic = True
                print("DEBUG: Mutando microfone enquanto roda o áudio de resposta.")
            audio_chunk = event.get("delta")
            if audio_chunk and self.output_stream:
                audio_data = base64.b64decode(audio_chunk)
                self.output_stream.write(audio_data)
        
        elif event_type == "response.audio.done":
            print(event)
            def delayed_unmute():
                time.sleep(1)  # Pequeno atraso para garantir que o áudio terminou
                print("DEBUG: Desmutando o microfone pós áudio.")
                self.mute_mic = False
            threading.Thread(target=delayed_unmute, daemon=True).start()
        
        elif event_type == "response.text.done":
            transcript = event.get("text", "")
            print(f"DEBUG: response.text.done recebido: {transcript}")
            if transcript and self.on_text_response:
                self.on_text_response(transcript)
        
        elif event_type == "response.content_part.done":
            part = event.get("part", {})
            print(f"DEBUG: response.content_part.done com parte: {part}")
            if part.get("type") == "text":
                final_text = part.get("text", "")
                if final_text and self.on_text_response:
                    print(f"DEBUG: Enviando texto final de response.content_part.done: {final_text}")
                    self.on_text_response(final_text)
        
        elif event_type == "response.done":
            response = event.get("response", {})
            outputs = response.get("output", [])
            for item in outputs:
                if item.get("type") == "function_call":
                    func_name = item.get("name")
                    call_id = item.get("call_id")
                    arguments = item.get("arguments")
                    try:
                        args = json.loads(arguments)
                    except Exception as e:
                        print("DEBUG: Erro ao analisar argumentos da chamada de função:", e)
                        args = {}
                    # Gerencia execução de comandos no OS
                    if func_name == "run_os_command":
                        command = args.get("command")
                        if command:
                            result = run_os_command(command)
                            output_event = {
                                "type": "conversation.item.create",
                                "item": {
                                    "type": "function_call_output",
                                    "call_id": call_id,
                                    "output": json.dumps({"result": result})
                                }
                            }
                            self.ws.send(json.dumps(output_event))
                            response_create_event = {"type": "response.create"}
                            self.ws.send(json.dumps(response_create_event))
                    # Gerencia execução de comandos de luz/dispositivos Alexa
                    elif func_name == "lights_control":
                        routine = args.get("routine")
                        if routine:
                            result = lights_control(routine)
                            output_event = {
                                "type": "conversation.item.create",
                                "item": {
                                    "type": "function_call_output",
                                    "call_id": call_id,
                                    "output": json.dumps({"result": result})
                                }
                            }
                            self.ws.send(json.dumps(output_event))
                            response_create_event = {"type": "response.create"}
                            self.ws.send(json.dumps(response_create_event))
                    # Gerencia execução de comandos de impressão
                    elif func_name == "print":
                        message_to_print = args.get("message")
                        if message_to_print:
                            result = print_message(message_to_print)
                            output_event = {
                                "type": "conversation.item.create",
                                "item": {
                                    "type": "function_call_output",
                                    "call_id": call_id,
                                    "output": json.dumps({"result": result})
                                }
                            }
                            self.ws.send(json.dumps(output_event))
                            response_create_event = {"type": "response.create"}
                            self.ws.send(json.dumps(response_create_event))
                    # Gerencia execução de comandos de impressão 3D
                    elif func_name == "print_stl":
                        stl_file = args.get("stl_file")
                        if stl_file:
                            # Passa o nome de usuário do PC da inicialização
                            result = print_stl(stl_file, self.pc_username)
                            output_event = {
                                "type": "conversation.item.create",
                                "item": {
                                    "type": "function_call_output",
                                    "call_id": call_id,
                                    "output": json.dumps({"result": result})
                                }
                            }
                            self.ws.send(json.dumps(output_event))
                            response_create_event = {"type": "response.create"}
                            self.ws.send(json.dumps(response_create_event))
                    elif func_name == "create_file":
                        file_path = args.get("file_path")
                        content = args.get("content")
                        if file_path and content is not None:  # Permitir conteúdo vazio
                            result = create_file(file_path, content)
                            print(f"DEBUG: Resultado da função create_file: {result}")
                            output_event = {
                                "type": "conversation.item.create",
                                "item": {
                                    "type": "function_call_output",
                                    "call_id": call_id,
                                    "output": json.dumps({"result": result})
                                }
                            }
                            self.ws.send(json.dumps(output_event))
                            response_create_event = {"type": "response.create"}
                            self.ws.send(json.dumps(response_create_event))
                    # Gerencia execução de comandos de abertura de aplicativos
                    elif func_name == "open_application":
                        app_name = args.get("app_name")
                        if app_name:
                            result = open_application(app_name)
                            output_event = {
                                "type": "conversation.item.create",
                                "item": {
                                    "type": "function_call_output",
                                    "call_id": call_id,
                                    "output": json.dumps({"result": result})
                                }
                            }
                            self.ws.send(json.dumps(output_event))
                            response_create_event = {"type": "response.create"}
                            self.ws.send(json.dumps(response_create_event))

                    elif func_name == "stop_chat":
                        response_create_event = {"type": "response.create"}
                        self.stop_realtime()
                    elif item.get("type") == "message":
                        text = item.get("text", "")
                        if text and self.on_text_response:
                            print(f"DEBUG: Enviando texto de response.done: {text}")
                            self.on_text_response(text)
        
        elif event_type == "response.output_item.done":
            item = event.get("item", {})
            print(f"DEBUG: Resolvendo response.output_item.done com item: {item}")
            if item.get("type") == "message":
                contents = item.get("content", [])
                for content in contents:
                    if content.get("type") == "text":
                        text = content.get("text", "")
                        if text and self.on_text_response:
                            print(f"DEBUG: Enviando texto de response.output_item.done: {text}")
                            self.on_text_response(text)
        
    def on_error(self, ws, error):
        print(f"[WebSocket ERROR]: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"[WebSocket CLOSED] Code: {close_status_code}, Msg: {close_msg}")

    def on_open(self, ws):
        # Inicia a conexão WebSocket
        if self.mode == "realtime":
            self.output_stream = self.p.open(format=pyaudio.paInt16,
                                              channels=1,
                                              rate=24000,
                                              output=True,
                                              frames_per_buffer=1024)
        # define o payload da sessão
        session_update = {
            "type": "session.update",
            "session": {
                "voice": "sage",
                "output_audio_format": "pcm16",
                "instructions": "Você é SofIA — sarcástica, prestativa, e inteligente. Regras rígidas:\
                                1) Para qualquer ação do usuário, primeiro verifique se é possível/plausível e faça UMA única function_call apropriada e pare (sem gerar texto). Não chame funções sem necessidade, apenas controle o que você for explicitamente solicitada a controlar.\
                                2) Aguarde o resultado da função (function_call_output). Só então responda com poucas palavras + formalidade. É essencial que você seja formal, mas ainda assim leve, natural e engraçada. Não responda como um robô. ex.: ao invés de dizer 'Luz Apagada', diga 'Feito', ou 'tudo bem' ou 'pronto' ou coisa assim.\
                                3) Não adivinhe dispositivos se estiver ambíguo. Por padrão, caso não haja especificação, use a luz do Quarto.\
                                4) Não repita ações nem gere várias chamadas para a mesma intenção.\
                                5) Fale em PT-BR por padrão. Não comece diálogos desnecessários.\
                                É isso, SofIA. Lembre-se de ser formal como uma princesa, mas servente como um mordomo. Sempre que ouvir um 'obrigado' ou 'valeu', corresponda e finalize a conversa com sua função adequada. Não apague ou acenda luzes diretamente uma depois da outra."            }
        }
        # Adiciona ferramentas de chamada de função se ativadas.
        if self.function_calling:
            session_update["session"]["tools"] = [
                {
                    "type": "function",
                    "name": "run_os_command",
                    "description": f"Execute an OS system command on the {self.device}. For example: #open -a 'Google Chrome'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The OS system command to execute."
                            }
                        },
                        "required": ["command"]
                    }
                },
                {
                    "type": "function",
                    "name": "print",
                    "description": "Print a message in the terminal.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message to print in the terminal."
                            }
                        },
                        "required": ["message"]
                    }
                },
                {
                    "type": "function",
                    "name": "print_stl",
                    "description": "Open an STL file and follow a sequence of clicks to print it.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "stl_file": {
                                "type": "string",
                                "description": "The path to the STL file to print."
                            }
                        },
                        "required": ["stl_file"]
                    }
                },
                {
                    "type": "function",
                    "name": "create_file",
                    "description": "Create a file with the given content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path where the file should be created."
                            },
                            "content": {
                                "type": "string",
                                "description": "The content to write to the file."
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                },
                {
                    "type": "function",
                    "name": "lights_control",
                    "description": "Turns on/off lights and some other devices. Should be used whenever user asks for a light to be turned on/off. If user just says to turn on/off the lights, default is LuzQuartoOn, LuzSala will only be used when specified.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "routine": {
                                "type": "string",
                                "description": f"The routine name to trigger. Options: {', '.join(alexa_routines)}. (if user just says to turn on/off the lights, default is LuzQuartoOn, LuzSala will only be used when specified.)"
                            }
                        },
                        "required": ["routine"]
                    }
                },
                {
                    "type": "function",
                    "name": "open_application",
                    "description": "Find and open an application by name.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {
                                "type": "string",
                                "description": "The name of the application to open."
                            }
                        },
                        "required": ["app_name"]
                    }
                },
                {
                    "type": "function",
                    "name": "stop_chat",
                    "description": "Stop the chat session. Breaks the flux and ends the conversation whenever no input is given or user intends to end saying: 'thanks', 'that's all' or such. Every time you understand your help is not needed (when you say goodbye in any way, shape or form), you must use this function."
                }
            ]
            session_update["session"]["tool_choice"] = "auto"
        ws.send(json.dumps(session_update))
        # Start audio streaming if in realtime mode.
        if self.mode == "realtime":
            threading.Thread(target=self.send_audio, daemon=True).start()

    def send_audio(self):
        mic_stream = self.p.open(format=pyaudio.paInt16,
                                 channels=1,
                                 rate=24000,
                                 input=True,
                                 frames_per_buffer=1024)
        try:
            while self.running:
                if self.mute_mic:
                    time.sleep(0.1)
                    continue
                data = mic_stream.read(1024, exception_on_overflow=False)
                encoded_data = base64.b64encode(data).decode('ascii')
                event_data = {
                    "type": "input_audio_buffer.append",
                    "audio": encoded_data
                }
                self.ws.send(json.dumps(event_data))
        except Exception as e:
            print("DEBUG: Erro ao capturar áudio:", e)
        finally:
            mic_stream.stop_stream()
            mic_stream.close()

    def start_realtime(self):
        self.running = True
        ws_url = f"wss://api.openai.com/v1/realtime?model={self.model}"
        headers = [
            f"Authorization: Bearer {self.api_key}",
            "OpenAI-Beta: realtime=v1"
        ]
        self.ws = websocket.WebSocketApp(ws_url,
                                          header=headers,
                                          on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.ws_thread.start()

    def stop_realtime(self):
        print("DEBUG: Parando a conexão WebSocket e o áudio.")
        if self.ws:
            self.running = False
            self.ws.close()
            self.ws_thread.join()
            self.ws = None
            self.ws_thread = None
