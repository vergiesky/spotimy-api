FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]