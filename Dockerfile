FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY Pipfile /code/

RUN pip install --upgrade pip \
    && pip install pipenv \
    && pipenv install

COPY . /code/
