FROM python:3.9-alpine
EXPOSE 80
WORKDIR /src
COPY . .
RUN pip install -r requirements.txt
CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80" ]
