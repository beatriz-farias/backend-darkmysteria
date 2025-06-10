# Dockerfile

# 1. Imagem base: Escolha uma imagem oficial do Python com uma versão Linux
#    Python 3.11 é uma boa escolha, já que você usou 3.11.11 no Render
FROM python:3.11-slim-bookworm

# 2. Definir variáveis de ambiente para a aplicação Python
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# 3. Definir o diretório de trabalho dentro do contêiner
#    É para onde seu código será copiado
WORKDIR /app

# 4. Copiar o arquivo de requisitos e instalar as dependências Python
#    Isso aproveita o cache do Docker. Se requirements.txt não mudar, este passo é rápido.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Instalar pacotes de sistema necessários (ffmpeg e espeak)
#    - apt-get update: Atualiza a lista de pacotes
#    - apt-get install -y: Instala os pacotes
#    - --no-install-recommends: Evita a instalação de pacotes recomendados desnecessários
#    - rm -rf /var/lib/apt/lists/*: Limpa o cache apt para manter a imagem pequena
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg espeak && \
    rm -rf /var/lib/apt/lists/*

# 6. Copiar o restante do código da aplicação para o contêiner
#    O '.' no final significa copiar tudo do diretório atual do host para /app no contêiner
COPY . .

# 7. Definir o comando para iniciar a aplicação
#    Render irá usar isso como o comando de início.
#    Uvicorn precisa de 0.0.0.0 para ouvir conexões de fora do contêiner
#    $PORT é uma variável de ambiente que o Render injeta automaticamente
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# NOTA: Certifique-se de que o seu requirements.txt esteja limpo,
# e não inclua pacotes específicos do Windows como pywin32.
# Certifique-se de que seu código utils.py NÃO está procurando por piper.exe
# Se você está usando pyttsx3, ele usará o 'espeak' que será instalado aqui.