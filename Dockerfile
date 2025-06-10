# Dockerfile

# 1. Imagem base:
FROM python:3.11-slim-bookworm

# 2. Definir variáveis de ambiente para a aplicação Python
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# 3. Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# 4. Copiar o arquivo de requisitos e instalar as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- NOVO: Instalar eSpeak (ainda é bom ter para fallback se pyttsx3 usar) ---
# E os pacotes de sistema necessários como ffmpeg.
# Remova 'espeak' daqui se você tiver certeza que pyttsx3 não o usará mais
# e quiser uma imagem menor. Mas para garantir, podemos deixá-lo.
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg espeak && \ 
    rm -rf /var/lib/apt/lists/*

# 6. Copiar o restante do código da aplicação para o contêiner
COPY . .

# --- NOVO: Definir variáveis de ambiente para o Piper ---
# Estes são os caminhos DENTRO do contêiner onde o Piper estará.
ENV PIPER_EXECUTABLE_PATH="/app/voices/piper"
ENV PIPER_VOICE_MODEL="/app/voices/pt_BR-faber-medium.onnx"
ENV PIPER_SAMPLE_RATE="22050" 

# --- NOVO: Tornar o executável do Piper executável ---
# É essencial no Linux dar permissão de execução ao binário que copiamos.
RUN chmod +x ${PIPER_EXECUTABLE_PATH}

# 7. Definir o comando para iniciar a aplicação
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
