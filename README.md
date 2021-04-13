# Testing Python FastAPI

## Dependencies
python >= 3.9


## Use Docker

### Install with docker-compose
Move to app folder then run:
```bash
docker-compose -f docker-compose.yml up
```

Go to http://127.0.0.1:8000/

## Manual installation without docker

### make sure the postgresql server is up and edit DB_CONFIG in the settings.py file correctly
### use DB_CONFIG.host instead of DOCKER_DB_HOST, in app/models//storage/database.py file line 15

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
