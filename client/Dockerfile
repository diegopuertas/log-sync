FROM python:3.12-slim

WORKDIR /app

RUN apt update && apt install -y iputils-ping procps 

COPY client.py requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["python", "-u", "client.py"]