FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential gcc && \
    pip install --upgrade pip && \
    pip install wheel

COPY . /app

RUN pip install -r shopping_app/requirements.txt

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=shopping_app/run.py
ENV PORT=5000

CMD gunicorn run:app --chdir shopping_app --bind 0.0.0.0:$PORT
