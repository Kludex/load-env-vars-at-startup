<h1 align="center">
    <strong>load-env-vars-at-startup</strong>
</h1>
<p align="center">
    <a href="https://github.com/Kludex/load-env-vars-at-startup" target="_blank">
        <img src="https://img.shields.io/github/last-commit/Kludex/load-env-vars-at-startup" alt="Latest Commit">
    </a>
        <img src="https://img.shields.io/github/workflow/status/Kludex/load-env-vars-at-startup/CI">
        <img src="https://img.shields.io/codecov/c/github/Kludex/load-env-vars-at-startup">
    <br />
    <a href="https://pypi.org/project/load-env-vars-at-startup" target="_blank">
        <img src="https://img.shields.io/pypi/v/load-env-vars-at-startup" alt="Package version">
    </a>
    <img src="https://img.shields.io/pypi/pyversions/load-env-vars-at-startup">
    <img src="https://img.shields.io/github/license/Kludex/load-env-vars-at-startup">
</p>

To understand the **motivation** behind this package, you might want to read about [fail fast](https://www.martinfowler.com/ieeeSoftware/failFast.pdf).

What this package does is to make sure you are reading all the environment variables at startup.

## Example

Consider that you have a folder with the following structure:

```
app/
├── __init__.py
└── main.py
```

Inside of `main.py` you have:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    name = os.environ["APP_NAME"]
    return {"message": f"Hello, {name}!"}
```

If you run this application, it will run without any problem, but if you forget to set the `APP_NAME` environment variable,
you will get an error when you try to access the `/` endpoint.

To avoid this, you can use this package.

If you decide to use it, your folder structure will look like this:

```
app/
├── __init__.py
├── main.py
└── config.py
```

Your `config.py` will look like this:

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str

settings = Settings()
```

And your `main.py` will look like this:

```python
from fastapi import FastAPI
from app.config import settings

app = FastAPI()

@app.get("/")
def index():
    name = settings.APP_NAME
    return {"message": f"Hello, {name}!"}
```

## Installation

You can install `load-env-vars-at-startup` via [pip](https://pypi.org/project/pip/):

```bash
pip install load-env-vars-at-startup
```

## Usage

```bash
levas DIR
```

Where `DIR` is the directory of your application.

## License

This project is licensed under the terms of the MIT license.
