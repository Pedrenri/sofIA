import speech_recognition as sr
import time
from sofia_client import get_sofia_client

def listen_for_wake_word():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    sofia_client = get_sofia_client()

    print("🔊 Ouvindo por wake-word...")

    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio, language="pt-BR").lower()

                    if "sofia" in command:
                        print("🔊 Ouvindo por wake-word...")
                        sofia_client.start_realtime()
                        time.sleep(0.2)  # aguarda a conexão se necessário

                        # Prompt inicial para iniciar a conversa
                        sofia_client.send_text_message("Sofia! (responda em PT-BR)")

                        # Escuta ativa por 10 segundos
                        timeout = time.time() + 10
                        while True:
                            if time.time() > timeout:
                                print("⏳ Tempo esgotado. Voltando ao modo passivo...")
                                print("🔊 Ouvindo por wake-word...")
                                sofia_client.stop_realtime()
                                break

                            try:
                                print("🎧 Aguardando comando...")
                                audio_cmd = recognizer.listen(source, timeout=10)
                                command = recognizer.recognize_google(audio_cmd, language="pt-BR").lower()
                                print(f"🗣️ Comando detectado: {command}")
                                timeout = time.time() + 10
                            except sr.WaitTimeoutError:
                                pass
                            except sr.UnknownValueError:
                                pass
                            except sr.RequestError as e:
                                print(f"Erro no reconhecimento: {e}")
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"Erro no reconhecimento: {e}")
    except KeyboardInterrupt:
        print("\nListener finalizado pelo usuário")
