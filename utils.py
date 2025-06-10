import subprocess
import speech_recognition as sr
from pydub import AudioSegment
import os
import io

def convert_audio_to_wav(audio_file_path: str) -> io.BytesIO:
    try:
        audio = AudioSegment.from_file(audio_file_path)
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0) # Voltar ao início do buffer
        return wav_buffer
    except Exception as e:
        raise Exception(f"Erro ao converter áudio para WAV: {e}. Certifique-se de que ffmpeg está instalado e no PATH.")

def audio_to_text(audio_file_path: str) -> str:
    r = sr.Recognizer()
    question = ""

    if not audio_file_path.lower().endswith('.wav'):
        try:
            wav_buffer = convert_audio_to_wav(audio_file_path)
            audio_source = sr.AudioFile(wav_buffer)
        except Exception as e:
            print(f"Erro na conversão de áudio, tentando abrir diretamente: {e}")
            audio_source = sr.AudioFile(audio_file_path) # Tenta abrir diretamente se a conversão falhar
    else:
        audio_source = sr.AudioFile(audio_file_path)
    
    try:
        with audio_source as source:
            r.adjust_for_ambient_noise(source) # Ajusta para o ruído ambiente
            audio = r.record(source) # Lê o arquivo de áudio inteiro
        text = r.recognize_google(audio, language="pt-BR") # Usando Google Web Speech API
        print(f"Áudio transcrito: {text}")
        return text
    except sr.UnknownValueError:
        print("Speech Recognition não conseguiu entender o áudio.")
        return ""
    except sr.RequestError as e:
        print(f"Erro no serviço de Speech Recognition; {e}")
        return ""
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a transcrição: {e}")
        return ""
    
def text_to_audio_bytes(text: str) -> bytes:
    """
    Converte texto em áudio usando Piper TTS (offline).
    Chama o executável Piper via subprocess usando variáveis de ambiente.
    """
    # NOVO: Ler os caminhos de variáveis de ambiente do Dockerfile
    piper_executable_path = os.getenv("PIPER_EXECUTABLE_PATH")
    piper_voice_model = os.getenv("PIPER_VOICE_MODEL")
    piper_sample_rate = int(os.getenv("PIPER_SAMPLE_RATE", "22050")) # Pega do ENV, com fallback

    if not piper_executable_path or not piper_voice_model:
        print("ERRO: Variáveis de ambiente PIPER_EXECUTABLE_PATH ou PIPER_VOICE_MODEL não configuradas.")
        return b""

    try:
        # Comando para rodar Piper
        command = [
            piper_executable_path,
            '--model', piper_voice_model,
            '--output-raw'
        ]

        # Use subprocess.Popen para chamar o executável
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        raw_audio_data, stderr_output = process.communicate(input=text.encode('utf-8'))

        if process.returncode != 0:
            print(f"Erro ao executar Piper: {stderr_output.decode('utf-8').strip()}")
            return b""
        
        if len(raw_audio_data) == 0:
            print("AVISO: Piper não gerou dados de áudio raw. Verifique o texto de entrada ou o modelo.")
            return b""

        # Pydub para converter raw para MP3
        audio_segment = AudioSegment(
            raw_audio_data,
            frame_rate=piper_sample_rate,
            sample_width=2,
            channels=1
        )

        audio_buffer = io.BytesIO()
        audio_segment.export(audio_buffer, format="mp3")
        audio_buffer.seek(0)
        return audio_buffer.getvalue()

    except FileNotFoundError:
        print(f"ERRO: Executável do Piper não encontrado em '{piper_executable_path}'. Verifique o caminho no Dockerfile/ENV.")
        return b""
    except Exception as e:
        print(f"Erro ao gerar áudio de texto com Piper: {e}")
        return b""