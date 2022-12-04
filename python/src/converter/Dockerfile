FROM python:3.10-slim-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential ffmpeg \
    && pip install --no-cache-dir --upgrade pip 

WORKDIR /app

COPY . /app

RUN pip install --requirement requirements.txt


CMD ["python","consumer.py"]