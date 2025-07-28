FROM mcr.microsoft.com/devcontainers/python:3.12-bullseye

WORKDIR /workspace

COPY . .

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install

