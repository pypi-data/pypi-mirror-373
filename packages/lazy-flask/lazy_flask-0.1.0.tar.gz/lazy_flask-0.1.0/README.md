# lazy_flask

[![CI](https://github.com/wrl96/lazy_flask/actions/workflows/ci.yml/badge.svg)](https://github.com/wrl96/lazy_flask/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/wrl96/lazy_flask/branch/master/graph/badge.svg)](https://codecov.io/gh/wrl96/lazy_flask)
[![PyPI](https://img.shields.io/pypi/v/lazy_flask.svg)](https://pypi.org/project/lazy_flask/)
[![License](https://img.shields.io/github/license/wrl96/lazy_flask.svg)](./LICENSE)

English | [中文文档](docs/README_zh.md) | [Contributing Guide](docs/CONTRIBUTING.md)

## Introduction

`lazy_flask` is a lightweight toolkit that simplifies the Flask development process, helping you quickly build Python web applications.

Features:

- Based on Flask, fully compatible with all Flask features
- Very small codebase (<200 lines)
- Supports custom middleware

## Installation

```bash
pip install lazy_flask
```

## Quick Start

#### Initialize
```python
from lazy_flask import App

app = App(name='lazy_flask', endpoint='/query')
```
|Parameter|Type|Default|Description|
|---|---|---|---|
|name|str|lazy_flask|Flask app name|
|endpoint|str|/query|Interaction endpoint|

#### Register Module
```python
from lazy_flask import App, Module

module = Module('module')
app.register_module(module)
```
Module

|Parameter|Type|Default|Description|
|---|---|---|---|
|name|str| |Module name, must be unique|

register_module

|Parameter|Type|Default|Description|
|---|---|---|---|
|module|Module| |Register the module to App|

#### Register Function
```python
from lazy_flask import App, Module, APIResponse, APIError

@module.function('hello')
def hello(name: str = '') -> APIResponse:
    return APIResponse(data={'hello': name})

@module.function('oh')
def oh() -> APIResponse:
    return APIResponse(error=APIError(code=1, message='This is an error.'))
```
function

|Parameter|Type|Default|Description|
|---|---|---|---|
|name|str| |Function name, must be unique in the same module|

APIResponse

|Parameter|Type|Default|Description|
|---|---|---|---|
|data|dict|{}|Returned data|
|error|APIError|APIError()|Error information|

APIError

|Parameter|Type|Default|Description|
|---|---|---|---|
|code|int|0|Error code|
|message|str| |Error message|

#### Make a Request

```python
import requests

url = "http://{host}/query"

data = {
    "module": "module", 
    "function": "hello", 
    "args": {
        "name": "world"
    }
}

response = requests.request("POST", url, json=data)

print(response.text) # {"data": {"hello": "world"}, "error": {"code": 0, "msg": ""}}
```

## Advanced Usage

#### Middleware

Middleware can intercept requests and responses. For example, you can do permission checks or modify responses before returning.<br>
Just define a function that accepts a `Request` or `Response`. If you modify it, return the new object. If not, lazy_flask will continue with the original.

```python
# Permission check
import time

from lazy_flask import *
from flask import request as flask_request

info = Module('info')
app.register_module(info)

# Check request, only executed when tag contains 'login'
def login_middleware(request: APIRequest):
    user_id = request.args.get('id', None)
    if user_id is None:
        raise APIError(code=1, message='User id is none')
    token = flask_request.headers.get('Authorization', None)
    if token is None:
        raise APIError(code=2, message='Token is none')

info.register_middleware(Middleware(login_middleware, tag='login', weight=1, m_type=MiddlewareType.Request))

# Modify response, executed globally
def add_timestamp_middleware(response: APIResponse) -> APIResponse:
    response['timestamp'] = int(time.time() * 1000)
    return response

info.register_middleware(Middleware(add_timestamp_middleware, m_type=MiddlewareType.Response))

@info.function('info', tags=['login'])
def info():
    return APIResponse(data={'result': 'ok'})
```

Middleware

|Parameter|Type|Default|Description|
|---|---|---|---|
|function|Callable| |Middleware handler, must accept Request or Response|
|tag|str| |If set, only runs when decorator specifies the same tag, otherwise global|
|weight|int|1|Priority, larger runs earlier|
|m_type|MiddlewareType|MiddlewareType.Request|Middleware type (Request or Response)|

## Demo

```bash
pip3 install lazy_flask
pip3 install requests

python3 example/app.py
python3 example/req.py # run in another terminal
```