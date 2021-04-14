FROM python:3.9.4-alpine
EXPOSE 80
WORKDIR /src
COPY . .
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN export PATH=/usr/local/pgsql/bin:$PATH
RUN pip install -U pip
RUN pip install -r requirements.txt
CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80" ]
