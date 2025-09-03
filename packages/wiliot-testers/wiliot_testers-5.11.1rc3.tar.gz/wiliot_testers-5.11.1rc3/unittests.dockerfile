FROM python:alpine3.15

WORKDIR /app

COPY wiliot/requirements.txt .

RUN apk add gcc cmake g++ tk; \
    pip install -r requirements.txt
