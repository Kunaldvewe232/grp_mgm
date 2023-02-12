FROM python:3.9.6-slim-buster

RUN mkdir -p /app
COPY . /app
WORKDIR /app/Repl

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y wget
RUN apt-get install -y procps

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

CMD python3 main.py