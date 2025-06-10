# Dockerfile

# 1. Imagem base: Escolha uma imagem oficial do Python com uma versão Linux
FROM python:3.11-slim-bookworm

# 2. Definir variáveis de ambiente para a aplicação Python
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# 3. Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# 4. Copiar o arquivo de requisitos e instalar as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Instalar pacotes de sistema necessários (ffmpeg e espeak-ng)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg espeak-ng espeak-ng-data && \ 
    rm -rf /var/lib/apt/lists/*

# --- NOVO: Definir variáveis de ambiente para o Piper ---
# Estes são os caminhos DENTRO do contêiner onde o Piper estará.
# Eles podem ficar aqui em cima, pois são apenas definições de variáveis.
ENV PIPER_EXECUTABLE_PATH="/app/voices/piper"
ENV PIPER_VOICE_MODEL="/app/voices/pt_BR-faber-medium.onnx"
ENV PIPER_SAMPLE_RATE="22050" 

# 6. Copiar o restante do código da aplicação para o contêiner
#    O '.' no final significa copiar tudo do diretório atual do host para /app no contêiner
#    A pasta 'voices' e o 'piper' executável são copiados AQUI.
COPY . .

RUN ln -s /app/voices/libpiper_phonemize.so.1.2.0 /app/voices/libpiper_phonemize.so.1 && \
    ln -s /app/voices/libespeak-ng.so.1.52.0.1 /app/voices/libespeak-ng.so.1

# --- MOVIDO: Tornar o executável do Piper executável ---
# Agora, esta linha vem DEPOIS que o 'piper' executável já foi copiado para /app/voices.
RUN chmod +x ${PIPER_EXECUTABLE_PATH}

# 7. Definir o comando para iniciar a aplicação
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]