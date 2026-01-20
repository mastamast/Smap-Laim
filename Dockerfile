# Dockerfile para Bot de Telegram
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear volumen para la base de datos
VOLUME ["/app/data"]

# Comando para ejecutar el bot
CMD ["python", "bot.py"]
