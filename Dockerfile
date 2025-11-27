FROM python:3.11-slim

# Instalar dependências do sistema para OpenCV, dlib e face_recognition
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

EXPOSE 8501

# Rodar Streamlit
CMD ["streamlit", "run", "facepass/ui/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]