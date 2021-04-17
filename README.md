# Get started Python FastAPI

## Python version
python >= 3.9

## Use Docker

### Install with docker-compose

Move to app folder then run:
```bash
docker-compose -f docker-compose.yml up
```
Go to http://127.0.0.1:8000/

## Manual installation without docker

Move to app folder
```bash
cd app/
```

### Database

Connect to your postgres BD using ```psql```
```bash
psql -U {postgres_user} -p {port_5432} -h {host}
```

Then create DB ```fastapidb```
```bash
CREATE DATABASE fastapidb;
```

Then create table ```person``` and insert data.
Use for that init.sql file from ```app/api/api_v1/storage/init.sql```

Then Edit ```DB_CONFIG``` in the ```settings.py``` file correctly
You will find settings file in ```api_v1``` folder

### Install requirements
```bash
pip install -r requirements.txt
```

## Run the app
```bash
uvicorn main:app --reload
```
Go to http://127.0.0.1:8000/

## Run tests

```bash
pytest tests.py
```