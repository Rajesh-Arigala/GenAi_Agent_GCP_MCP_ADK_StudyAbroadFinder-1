FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y nodejs npm && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/reports
ENV REPORTS_DIR=/app/reports

EXPOSE 10000

CMD ["gunicorn", "--timeout", "180", "--bind", "0.0.0.0:10000", "app.server:app"]