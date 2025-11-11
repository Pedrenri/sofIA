import time
from sofia_client import get_sofia_client
import pvporcupine
import pyaudio
import struct
import dotenv
import os

def listen_for_wake_word():
    dotenv.load_dotenv()

    porcupine = pvporcupine.create(
        access_key=os.getenv("PICOVOICE_KEY"),
        keyword_paths=["./Sofia_pt_windows_v3_0_0.ppn"],
        model_path="porcupine_params_pt.pv"
    )

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    sofia_client = get_sofia_client()

    print("🔊 Esperando a palavra de ativação...")

    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm)
            if result >= 0:  # Wake word detectada
                print("🚀 Wake word detectada: Sofia")
                sofia_client.start_realtime()
                timeout = time.time() + 20
                
                while True:
                    if (time.time() > timeout and not sofia_client.mute_mic):
                        print("⏳ Tempo esgotado. Voltando a ouvir a palavra de ativação...")
                        sofia_client.stop_realtime()
                        break

                    if (not sofia_client.running):
                        print("❌ Finalizado. Voltando a ouvir a palavra de ativação...")
                        break

                    if sofia_client.mute_mic:
                        timeout = time.time() + 20

    except KeyboardInterrupt:
        print("\nListener finalizado pelo usuário")
    finally:
        audio_stream.close()
        pa.terminate()
        porcupine.delete()