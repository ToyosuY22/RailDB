FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY Pipfile /code/

RUN apt update \
    && apt -y upgrade \
    && apt -y install binutils libproj-dev gdal-bin=3.6.2+dfsg-1+b2 libgdal-dev=3.6.2+dfsg-1+b2

RUN pip install --upgrade pip \
    && pip install pipenv \
    && pipenv install

COPY . /code/
