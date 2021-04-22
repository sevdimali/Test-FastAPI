FROM python:3.9.4-slim-buster

LABEL maintainer="Eliam LOTONGA" email="contact@eliam-lotonga.fr"

EXPOSE 80

ENV DATABASE_HOST=api_db

ENV APP_EXPOSED_PORT=80

WORKDIR /src/app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pytest

CMD [ "python", "main.py" ]