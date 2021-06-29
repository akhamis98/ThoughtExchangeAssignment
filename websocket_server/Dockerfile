# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 8080
COPY . .

CMD [ "python", "app.py", "0.0.0.0", "8080"]