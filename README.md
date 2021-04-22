# Get started Python FastAPI

## Python versions

python >= 3.9

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

Note that, you can create a virtual environment
if you don't want to install requirements in your host machine

For that run the following commands

```bash
python -m venv {choose-name}
```

activate this virtual environment

Linux or Mac

```bash
source {choose-name}/bin/activate
```

Windows

```bash
bash ./{choose-name}/Scripts/activate
```

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

Then Edit `ENV` and `TORTOISE_ORM` variables in the `settings.py` correctly.
You will find settings file in `api/api_v1` folder

Then run migrations using aerich to create db table(s).

```bash
aerich init -t api.api_v1.settings.TORTOISE_ORM
```

```bash
aerich init-db
```

## Run the app

```bash
python main.py
```

Go to http://127.0.0.1:8000/

## Fake Data

To load some fake data, go to http://127.0.0.1:8000/data
which will load fake data and redirect you to /

## Run tests

```bash
pytest --cache-clear --disable-warnings -vv
```
