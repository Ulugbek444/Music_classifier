FROM python:3.11

RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip

# ✅ СТАВИМ CPU TORCH ПЕРВЫМ И БЕЗ ЗАВИСИМОСТЕЙ
RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .

# ✅ Остальные пакеты НЕ смогут подтянуть CUDA
RUN pip install \
    --no-cache-dir \
    --timeout 1000 \
    --retries 10 \
    -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "-c", "import uvicorn; print('UVICORN OK', uvicorn.__file__)"]


