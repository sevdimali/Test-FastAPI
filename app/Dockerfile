FROM python:3.9.4-slim-buster
EXPOSE 80
WORKDIR /src/app
COPY . .
RUN pip install -r requirements.txt
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80" ]