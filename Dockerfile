FROM python:3.6-buster

COPY setup.py /app/setup.py
WORKDIR /app

RUN python -m pip install -e .

ENTRYPOINT [ "cryb" ]