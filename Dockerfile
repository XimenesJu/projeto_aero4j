# Dockerfile para o backend (Render espera na raiz do repositório)
FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY backend/requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do backend
COPY backend/ .

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
