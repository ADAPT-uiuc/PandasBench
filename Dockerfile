FROM python:3.10.16

WORKDIR /home/ubuntu/

COPY runner/requirements.txt .

RUN apt-get update -q \
    && apt-get install -qy time openjdk-17-jdk-headless \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
