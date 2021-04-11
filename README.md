# Testing Python FastAPI

## Dependencies
python >= 3.9


## Docker installation

create docker image
```bash
docker build --tag {my-api}
```

run docker container
```bash
docker run -d --name {myApi} -p 8000:80 {my-api}
```

## Manual installation

Install requirements
```bash
pip install -r requirements.txt
```

## Run the app

```bash
uvicorn app:app --reload
```

Go to http://127.0.0.1:8000/
