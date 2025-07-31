FROM python:3.11-alpine

WORKDIR /app

# Instalar apenas dependências essenciais
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    git

# Copiar requirements primeiro (para cache)
COPY requirements.txt .

# Instalar dependências Python e limpar cache
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# Copiar apenas arquivos essenciais
COPY main.py .
COPY core/ ./core/
COPY models/ ./models/
COPY services/ ./services/
COPY api/ ./api/
COPY config/ ./config/
COPY utils/ ./utils/

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["python", "main.py"]
