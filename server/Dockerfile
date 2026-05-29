FROM python:3.12-slim

WORKDIR /app

RUN apt update && apt install -y iputils-ping procps 

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

ENTRYPOINT ["python", "-u", "server.py"]
