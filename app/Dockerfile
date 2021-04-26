FROM python:3.9.4-slim-buster

LABEL maintainer="Eliam LOTONGA" email="contact@eliam-lotonga.fr"

EXPOSE 80

ENV DATABASE_HOST=api_db

ENV APP_EXPOSED_PORT=80

WORKDIR /src/app

COPY ./requirements/common.txt .

RUN pip install --no-cache-dir --no-input -r common.txt

COPY . .

RUN rm requirements
CMD [ "python", "main.py" ]