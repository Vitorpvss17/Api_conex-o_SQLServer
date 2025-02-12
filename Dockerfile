# Use uma imagem base com Python
FROM python:3.9-slim

# Instale dependências necessárias
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get install -y unixodbc-dev \
    && apt-get clean

# Copie o código da aplicação para o contêiner
COPY . /app
WORKDIR /app

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para rodar a aplicação
CMD ["waitress-serve", "--call", "app:create_app"]
