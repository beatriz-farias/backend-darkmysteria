# Dockerfile

# 1. Imagem base: Python 3.11 em Debian Bookworm
FROM python:3.11-slim-bookworm

# 2. Definir variáveis de ambiente para a aplicação Python
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# 3. Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# 4. Copiar o arquivo de requisitos e instalar as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Instalar pacotes de sistema necessários (ffmpeg, espeak-ng e espeak-ng-data)
#    'espeak-ng-data' contém o arquivo 'phontab' e outros dados para o Piper.
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg espeak-ng espeak-ng-data && \
    rm -rf /var/lib/apt/lists/*

# --- NOVO: Definir variáveis de ambiente para o Piper ---
# Estes caminhos são DENTRO do contêiner.
# PIPER_EXECUTABLE_PATH: Caminho para o binário do Piper (copiado de 'voices/')
# PIPER_VOICE_MODEL: Caminho para o arquivo .onnx do modelo de voz
# PIPER_SAMPLE_RATE: A taxa de amostragem do modelo de voz (verifique no .onnx.json)
# PIPER_ESPEAK_DATA_PATH: ONDE espeak-ng-data instala seus dados (encontrado via depuração)
ENV PIPER_EXECUTABLE_PATH="/app/voices/piper"
ENV PIPER_VOICE_MODEL="/app/voices/pt_BR-faber-medium.onnx"
ENV PIPER_SAMPLE_RATE="22050" 
ENV PIPER_ESPEAK_DATA_PATH="/usr/lib/x86_64-linux-gnu/espeak-ng-data"
# 6. Copiar o restante do código da aplicação para o contêiner
#    Isso inclui a pasta 'voices/' com o 'piper' executável e os arquivos de modelo/bibliotecas.
COPY . .

# --- NOVO: Criar links simbólicos para as bibliotecas compartilhadas do Piper ---
# O executável 'piper' para Linux precisa dessas libs no PATH ou no mesmo diretório.
# Criamos links simbólicos da versão completa para o nome curto que o Piper procura.
RUN ln -s /app/voices/libpiper_phonemize.so.1.2.0 /app/voices/libpiper_phonemize.so.1 && \
    ln -s /app/voices/libespeak-ng.so.1.52.0.1 /app/voices/libespeak-ng.so.1 

RUN ln -s /usr/lib/x86_64-linux-gnu/espeak-ng-data /usr/share/espeak-ng-data


# --- NOVO: Tornar o executável do Piper executável ---
# É essencial dar permissão de execução ao binário copiado.
RUN chmod +x ${PIPER_EXECUTABLE_PATH}

# 7. Definir o comando para iniciar a aplicação
#    Uvicorn precisa de 0.0.0.0 para ouvir conexões de fora do contêiner.
#    $PORT é uma variável de ambiente que o Render injeta automaticamente.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]