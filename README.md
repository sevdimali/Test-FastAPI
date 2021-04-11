# Testing Python FastAPI

## Dependencies
python >= 3.9

## Manual installation

Install requirements
```bash
pip install -r requirements.txt
```
## Run the app
execute this command
```bash
uvicorn app:app --reload
```
Go to http://127.0.0.1:8000/


## Docker installation

Move to ```app``` folder
```bash
cd app
```

create docker image
```bash
docker build --tag {my-api}
```

run docker container
```bash
docker run --rm -d --name {myApi} -p 8000:80 {my-api}
```

Go to http://127.0.0.1:8000/
