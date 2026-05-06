FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p data assets/generated_carousels assets/fonts templates/carousel_templates

# Tornar scripts executáveis
RUN chmod +x scripts/*.py

# Expor porta do dashboard
EXPOSE 8501

# Comando padrão
CMD ["python", "main.py", "--mode", "dashboard"]