from fastapi import FastAPI
import json
app = FastAPI()


@app.get('/')
def index():
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@gmail.com"
    }
    return data


@app.get('/about')
def about():
    data = {'name': "About page"}
    return data
