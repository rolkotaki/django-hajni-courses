FROM python:3.12.1

ENV PYTHONUNBUFFERED 1

RUN mkdir /django_app
WORKDIR /django_app

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD . /django_app/
