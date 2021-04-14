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

### Database

Connect to your postgres BD using ```psql```
```bash
psql -U {postgres_user} -p {port_5432} -h {host}
```

Then create DB ```fastapidb```
```bash
CREATE DATABASE fastapidb;
```

Then create table ```person``` and insert data use init.sql file from ```app/models/storage/init.sql```

Edit ```DB_CONFIG``` in the ```settings.py``` file correctly

Then uncomment ```DB_CONFIG.host``` instead of ```DOCKER_DB_HOST``` line from ```app/models/storage/database.py file line 15```

### Install requirements
```bash
pip install -r requirements.txt
```
## Run the app
```bash
uvicorn app:app --reload
```
Go to http://127.0.0.1:8000/
