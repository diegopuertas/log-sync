FROM python:3.12-slim

WORKDIR /app

ARG ENVIRONMENT

RUN if [ -z "$ENVIRONMENT" ] || [ "$ENVIRONMENT" != "prod" ]; then \
      echo "Running non-prod step..."; \
      apt update && apt install -y iputils-ping procps; \
    else \
      echo "Running in the production environment"; \
    fi

COPY server.py requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["python", "-u", "server.py"]
