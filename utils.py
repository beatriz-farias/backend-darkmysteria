# utils.py
import speech_recognition as sr
from pydub import AudioSegment
import io
import os
import subprocess # Para chamar o executável do Piper
import tempfile   # Para lidar com arquivos temporários
import uuid       # Para gerar nomes únicos para arquivos temporários

# --- NOVO: Importar dotenv para carregar variáveis de ambiente (se o módulo for executado diretamente, útil para testes locais) ---
from dotenv import load_dotenv
load_dotenv()

# --- NOVO: Variáveis de Configuração do Piper (lidas de variáveis de ambiente do Dockerfile) ---
# Estes valores serão definidos no Dockerfile como ENV.
# Usamos os.getenv para lê-los em tempo de execução.
# O 'int()' e 'str()' são para garantir o tipo correto.
PIPER_EXECUTABLE_PATH_ENV = os.getenv("PIPER_EXECUTABLE_PATH")
PIPER_VOICE_MODEL_ENV = os.getenv("PIPER_VOICE_MODEL")
PIPER_SAMPLE_RATE_ENV = int(os.getenv("PIPER_SAMPLE_RATE", "22050")) # Converte para int, com fallback
PIPER_ESPEAK_DATA_PATH_ENV = os.getenv("PIPER_ESPEAK_DATA_PATH","/usr/lib/x86_64-linux-gnu/espeak-ng-data")


# --- Funções de Áudio (convert_audio_to_wav e audio_to_text - inalteradas) ---
def convert_audio_to_wav(audio_file_path: str) -> io.BytesIO:
    try:
        audio = AudioSegment.from_file(audio_file_path)
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        return wav_buffer
    except Exception as e:
        raise Exception(f"Erro ao converter áudio para WAV: {e}. Certifique-se de que ffmpeg está instalado e no PATH.")

def audio_to_text(audio_file_path: str) -> str:
    r = sr.Recognizer()
    text = ""

    if not audio_file_path.lower().endswith('.wav'):
        try:
            wav_buffer = convert_audio_to_wav(audio_file_path)
            audio_source = sr.AudioFile(wav_buffer)
        except Exception as e:
            print(f"Erro na conversão de áudio, tentando abrir diretamente: {e}")
            audio_source = sr.AudioFile(audio_file_path)
    else:
        audio_source = sr.AudioFile(audio_file_path)
    
    try:
        with audio_source as source:
            r.adjust_for_ambient_noise(source)
            audio = r.record(source)
        # Ainda usando Google Web Speech API (sem chave) para STT
        text = r.recognize_google(audio, language="pt-BR")
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
    
# --- Função text_to_audio_bytes (agora para Piper TTS) ---
def text_to_audio_bytes(text: str) -> bytes:
    """
    Converte texto em áudio usando Piper TTS (offline).
    Chama o executável Piper via subprocess usando variáveis de ambiente.
    """
    # NOVO: Verificar se as variáveis de ambiente essenciais estão definidas
    if not PIPER_EXECUTABLE_PATH_ENV or not PIPER_VOICE_MODEL_ENV:
        print("ERRO: Variáveis de ambiente do Piper (EXECUTABLE_PATH ou VOICE_MODEL) não configuradas.")
        return b""

    try:
        command = [
            PIPER_EXECUTABLE_PATH_ENV,
            '--model', PIPER_VOICE_MODEL_ENV,
            '--output-raw',
            '--espeak-data', PIPER_ESPEAK_DATA_PATH_ENV
        ]
        
        # NOVO: Adicionar a flag --espeak-data SE a variável estiver definida
        if PIPER_ESPEAK_DATA_PATH_ENV:
            command.extend(['--espeak-data', PIPER_ESPEAK_DATA_PATH_ENV])

        # Imprimir comando completo para debug (opcional, remova em produção)
        # print(f"DEBUG utils: Comando Piper: {' '.join(command)}")
        # print(f"DEBUG utils: Texto para Piper: '{text}'")

        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        raw_audio_data, stderr_output = process.communicate(input=text.encode('utf-8'))

        # Imprimir saída de erro e tamanho do áudio para debug (opcional, remova em produção)
        # print(f"DEBUG utils: Piper returncode: {process.returncode}")
        # print(f"DEBUG utils: Piper stderr (decoded): '{stderr_output.decode('utf-8').strip()}'")
        # print(f"DEBUG utils: Tamanho raw_audio_data: {len(raw_audio_data)} bytes")

        if process.returncode != 0:
            print(f"Erro ao executar Piper (código {process.returncode}): {stderr_output.decode('utf-8').strip()}")
            return b""
        
        if len(raw_audio_data) == 0:
            print("AVISO utils: Piper não gerou nenhum dado de áudio raw. Verifique o texto de entrada ou o modelo.")
            return b""

        # Pydub para converter raw para MP3
        audio_segment = AudioSegment(
            raw_audio_data,
            frame_rate=PIPER_SAMPLE_RATE_ENV,
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