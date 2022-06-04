FROM python:3.10.2-bullseye


WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt
COPY . .


