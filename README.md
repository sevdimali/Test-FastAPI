# Get started Python FastAPI

## Python versions

python 3.7, 3.8 3.9

### Install with docker-compose

Move to the app folder

```bash
cd app
```

Then run:

```bash
docker-compose -f docker-compose.yml up
```

Go to http://127.0.0.1:8000/

## Manual installation without docker

Move to app folder

```bash
cd app/
```

### Install requirements

```bash
pip install -r requirements.txt
```

### Database

Connect to your postgres BD using `psql`

```bash
psql -U {postgres_user} -p {port_5432} -h {host}
```

Then create DB `fastapidb`

```bash
CREATE DATABASE fastapidb;
```

Then Edit `TORTOISE_ORM` variable in the `settings.py` correctly.
You will find settings file in `api_v1` folder

Then create table `person`.
For that run this following commands

```bash
aerich init -t api.api_v1.settings.TORTOISE_ORM
```

```bash
aerich init-db
```

Note that the program will insert data by default
when you run the app and navigate to the root path /
if the `person` table is empty.
To avoid this, go to the app doc http://127.0.0.1:8000/api/v1/docs
and insert a first user using the post route

## Run the app

```bash
python main.py
```

Go to http://127.0.0.1:8000/

## Run tests

```bash
pytest tests.py
```
