# Environemnt As A Software

[![Package](https://github.com/ciuliene/eaasy/actions/workflows/CD.yml/badge.svg)](https://github.com/ciuliene/eaasy/actions/workflows/CD.yml) [![codecov](https://codecov.io/gh/ciuliene/eaasy/graph/badge.svg?token=KH72ECLJHF)](https://codecov.io/gh/ciuliene/eaasy)

Build an environment with a database and a REST API.

## Requirements

- Python 3.12
- PostgreSQL 13.4
- Redis 6.2.6 (optional but recommended)


## Initial setup

Create a database in PostgreSQL:

```sql
create database database_name;
```

Create a virtual environment and install the dependencies:

```sh
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Set the `environment variables`:
```
POSTGRES_URI=<SQL_DATABASE_URI>

# macOS only
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Optional for Redis
REDIS_URI=<REDIS_URI>
```

Initialize alembic:


```python
# alembic_init.py
from eaasy.extensions.migration import init
from argparse import ArgumentParser, Namespace as ArgumentNamespace

def get_arguments() -> ArgumentNamespace:
    parser = ArgumentParser(description='Alembic migration helper')
    parser.add_argument('sql_url', metavar='sql_url', type=str, help='SQLAlchemy URL')
    parser.add_argument('--path', '-p', metavar='path', type=str, help='Alembic path', default='src/alembic')
    parser.add_argument('--tables-folder', '-t', metavar='tables_folder', type=str, help='Tables folder', default='src/tables')

    args = parser.parse_args()

    if not args.sql_url:
        raise Exception('SQLAlchemy URL is required')

    return args

if __name__ == '__main__':
    args = get_arguments()
    init(args.sql_url, args.path, args.tables_folder)
```

Launch the script to build the alembic folder:

```sh
python alembic_init.py <SQL_DATABASE_URI> # --path src/alembic (optional)
```

Create a table:

```python
# src/tables/user.py
from eaasy import BaseEntity, Audit
from sqlalchemy import Column, String

class UserProperties:
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)


class User(BaseEntity, UserProperties, Audit):
    __tablename__ = 'users'
```

And add it to the `src/tables/__init__.py` file:

```python
# src/tables/__init__.py
from .user import User

__all__ = ['User']
```

Run the migration:

```sh
alembic revision --autogenerate -m "Create users table"
alembic upgrade head
```

## Run the application

Create a main module:

```python
# app.py

from eaasy import Eaasy, GunEaasy
from eaasy.extensions import buil_model, build_resource
from src.tables.user import User, UserProperties

api = Eaasy(
    name=__name__,
    title='API',
    version='1.0',
    description='A simple API',
    doc='/swagger'
)

# Create models for User resource (GET, POST and PUT)
user_ns, get_model = buil_model(User)
user_ns, upsert_model = buil_model(UserProperties, namespace=user_ns)

# Build and register resource
build_resource(User, user_ns, get_model, upsert_model)

# # Add namespace to API
api.add_namespace(user_ns)

app = api.get_app() # Required if you want to perform flask operations

if __name__ == '__main__':
    options = {
        'bind': '%s:%s' % ('0.0.0.0', '8080'),
        'workers': 1
    }
    GunEaasy(app, options).run()
```

Run the application:

```sh
python app.py
# or
gunicorn app:app
# or
flask run
```

## Features

### Custom endpoints

By default the `build_resource` method build a resource with these enabled endpoints:

- `get_all` -> GET /entity/ # Get all entities
- `post` -> POST /entity/ # Create new entity
- `get_by_id` -> GET /entity/<id:int> # Get entity by id
- `put` -> PUT /entity/<id:int> # Edit entity by id
- `delete` -> DELETE /entity/<id:int> # Delete entity by id

You can disable one or more endpoints by setting to `False` the correspoing key, for instance:

```python
# Build resource without get_by_id endpoint
build_resource(User, user_ns, get_model, upsert_model, get_by_id=False)
```

### Callbacks

You can add callbacks to the resources:

```python
def after_post(data):
    print(data.firstName) # 'data' represent the model of the object created after the POST request

build_resource(User, user_ns, get_model, upsert_model, on_post=after_post)
```

Available callbacks:
- `on_post`
- `on_put`
- `on_delete`

### Limit rate

API requests can be limited by the number of requests in an interval of time. 

NOTE: the application should be running with Redis properly configured. See `environment variables` in [Initial setup](#initial-setup) section.

You can enable limiter using `enable_limiter` parameters:

```python
api = Eaasy(
    name=__name__,
    title='API',
    version='1.0',
    description='A simple API',
    doc='/swagger',
    enable_limiter=True
)
```

And set the limit for all methods:

```python
build_resource(User, user_ns, get_model, upsert_model, limit='5 per minute')
```

Or specify a limit for each method:

```python
build_resource(User, user_ns, get_model, upsert_model, get_all_limit='5 per minute')
```

Available arguments:
- `get_all_limit`
- `get_by_id_limit`
- `post_limit`
- `put_limit`
- `delete_limit`

### Logger

By providing `logger` parameter in `Eaasy` class you can:

```python
api = Eaasy(
    logger=True # Configure default logger
)
```

```python
api = Eaasy(
    logger=custom_logger # Or provide your own logger
)
```

And you can also extract and wherever you want (especially if you want to use the default one):

```python
logger = api.logger # This raises an exception if not configured
```

### OpenIDConnect (from `flask_oidc`)

Same for the OpenIdConnet instance:

```python
api = Eaasy(
    oidc=True # Configure default OIDC
)
```

```python
api = Eaasy(
    oidc=OpenIDConnect(app) # Or provide your own OIDC (OpenIDConnect from flask_oidc package only)
)
```

Extract and use it:

```python
oidc = api.oidc # This raises an exception if not configured
```

Refer to [flask_oidc](https://flask-oidc.readthedocs.io/en/latest/) docs for OpenIDConnect configuration (make sure that the installed version matches the version described in the docs).

You can set the `accept_token` decorator for all methods:

```python
build_resource(User, user_ns, get_model, upsert_model, oidc=app.oidc)
```

Or specify the `accept_token` decorator for each method:

```python
build_resource(User, user_ns, get_model, upsert_model, get_all_oidc=app.oidc)
```

Available arguments:
- `get_all_oidc`
- `get_by_id_oidc`
- `post_oidc`
- `put_oidc`
- `delete_oidc`

To introduce other decorators please create your own resource and set the required decorators. 

Refer to [flask_restx](https://flask-restx.readthedocs.io/en/latest/) docs for decorators configuration (make sure that the installed version matches the version described in the docs).