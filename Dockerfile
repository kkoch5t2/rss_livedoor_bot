FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Tokyo

RUN apt-get update && apt-get install -y --no-install-recommends     gcc     g++     libxml2-dev     libxslt-dev     libjpeg-dev     zlib1g-dev     libpng-dev     git     curl     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip &&     pip install --no-cache-dir -r requirements.txt

# newspaper3k/4k用
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')" || true

COPY . .

CMD ["python", "-m", "src.main", "--once"]
