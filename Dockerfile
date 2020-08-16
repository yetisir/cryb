FROM python:3.6-buster

RUN mkdir /app
WORKDIR /app
COPY requirements.txt .

RUN python -m pip install -r requirements.txt


COPY setup.py .
COPY cryb cryb/
RUN python -m pip install -e .

RUN groupadd -r cryb && useradd --no-log-init -r -g cryb cryb

USER cryb