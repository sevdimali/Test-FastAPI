# Get started Python FastAPI

[![codecov](https://codecov.io/gh/meschac38700/Test-FastAPI/branch/master/graph/badge.svg?token=iffvr8Fmg5)](https://codecov.io/gh/meschac38700/Test-FastAPI)
[![Workflow](https://github.com/meschac38700/Test-FastAPI/actions/workflows/workflow.yml/badge.svg?branch=master)](https://github.com/meschac38700/Test-FastAPI/actions/workflows/workflow.yml)
[![Lint](https://github.com/meschac38700/Test-FastAPI/actions/workflows/auto-format.yaml/badge.svg)](https://github.com/meschac38700/Test-FastAPI/actions/workflows/auto-format.yaml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pypi](https://img.shields.io/pypi/v/pip.svg)](https://pypi.org/project/pip/)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![CC-0 license](https://img.shields.io/badge/License-CC--0-blue.svg)](https://github.com/meschac38700/Test-FastAPI/blob/master/LICENSE)

## Client code

[Client App](https://github.com/meschac38700/fastAPI-client-side)

## Python versions

### >= 3.9

## Install with docker-compose

Then run:

```bash
docker-compose -f docker-compose.yml up
```

The app running on http://127.0.0.1:8000/

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

### Install requirements

Upgrade `pip`

```bash
pip install --upgrade pip
```

install application requirements

```bash
pip install -r  requirements/common.txt
```

install dev requirements (useful to run tests)

```bash
pip install -r requirements/dev.txt
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
You will find settings file in `app/api/api_v1` folder

Then run migrations using `aerich` command to create table(s).

```bash
aerich init -t app.api.api_v1.settings.TORTOISE_ORM
```

```bash
aerich init-db
```

## Run the app

```bash
python main.py
```

The app running on http://127.0.0.1:8000/

## Fake Data

To load some fake data, go to http://127.0.0.1:8000/data
which will load fake data and redirect you to the app root `/`

## Run all the tests

from root folder run (Test-FastAPI):

```bash
pytest
```
