import speech_recognition as sr
import time
from sofia_client import get_sofia_client

def listen_for_wake_word():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 10
    mic = sr.Microphone()
    sofia_client = get_sofia_client()

    keywords = ["sophia", "sofia", "fia", "sophie", "sofie"]

    print("🔊 Esperando a palavra de ativação...")

    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_faster_whisper(audio, model="small", language="pt").lower()
                    print(f"🔊 Comando reconhecido: {command}")
                    if any(keyword in command for keyword in keywords):
                        sofia_client.start_realtime()
                        time.sleep(0.7)  # aguarda a conexão se necessário

                        # Prompt inicial para iniciar a conversa
                        sofia_client.send_text_message(command + "(responda em PT-BR)")

                        # Escuta ativa por 8 segundos
                        timeout = time.time() + 8
                        while True:
                            if time.time() > timeout and not sofia_client.mute_mic:
                                print("⏳ Tempo esgotado. Voltando a ouvir a palavra de ativação...")
                                sofia_client.stop_realtime()
                                break

                            if sofia_client.mute_mic:
                                timeout = time.time() + 8

                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"Erro no reconhecimento: {e}")
    except KeyboardInterrupt:
        print("\nListener finalizado pelo usuário")