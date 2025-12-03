FROM python:3.11-slim

WORKDIR /app

# системные зависимости (минимум)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# зависимости бота
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# код
COPY . .

CMD ["python", "app.py"]
