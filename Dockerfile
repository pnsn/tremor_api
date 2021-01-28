FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1
RUN mkdir /app
COPY ./requirements/ /app/requirements/

RUN apk add --update --no-cache postgresql-libs jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN pip install -r /app/requirements/local.txt

RUN apk del .tmp-build-deps

WORKDIR /app
COPY ./app/ /app

RUN adduser -D user

USER user
EXPOSE 5000