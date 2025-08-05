FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential gcc g++ libpq-dev libssl-dev libffi-dev python3-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

COPY scripts/ ./scripts/
COPY data/ ./data/
RUN mkdir -p faqs_markdown pages posts

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000
CMD ["python", "railway_config.py"]
