FROM python:3.9.4-slim-buster

LABEL maintainer="Eliam LOTONGA" email="contact@eliam-lotonga.fr"

EXPOSE 80

WORKDIR /src/app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pytest --cache-clear --disable-warnings -vv tests/tests.py

CMD [ "python", "main.py" ]