
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY . .

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV PREFECT_HOME=/app/prefect

ENV PREFECT_API_DATABASE_CONNECTION_URL=postgresql+asyncpg://root:root@postgres_db:5432/mydatabase

ENV PREFECT_API_URL=http://0.0.0.0:4200/api

EXPOSE 4200

ENTRYPOINT ["/app/entrypoint.sh"]
