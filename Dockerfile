FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt /app/
RUN apt-get update && \
    apt-get install -y gcc && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y gcc && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY . /app/
RUN useradd -m appuser
USER appuser
CMD ["python", "app.py"]