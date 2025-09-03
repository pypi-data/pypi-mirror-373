# QAnswer Python SDK

[![PyPI version](https://badge.fury.io/py/qanswer-sdk.svg)](https://pypi.org/project/qanswer-sdk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/qanswer-sdk.svg)](https://pypi.org/project/qanswer-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Official **Python SDK** for the [QAnswer API](https://qanswer.eu), automatically generated from the OpenAPI specification.

This SDK allows Python applications to interact with QAnswer's services programmatically without needing to craft raw HTTP requests.

---

## 🚀 Features

- Full coverage of QAnswer API endpoints  
- Type-safe models via [Pydantic](https://docs.pydantic.dev)  
- Easy configuration of authentication and base URL  
- Auto-generated and versioned with each API release  

---

## 📦 Installation

You can install from [PyPI](https://pypi.org/project/qanswer-sdk/):

```bash
pip install qanswer-sdk
```


Or add it to your `requirements.txt`

```txt
qanswer-sdk==3.1184.0
```

---

## 🔑 Authentication

Most endpoints require authentication. You can set your API key like this:
```python
from qanswer_sdk import Configuration, ApiClient
from qanswer_sdk.apis import DefaultApi

# Configure API key authorization
config = Configuration(
    host="https://api.qanswer.eu",
    api_key={"Authorization": "Bearer <YOUR_TOKEN>"}
)

# Initialize client
with ApiClient(config) as client:
    api = DefaultApi(client)
    response = api.health_check()
    print(response)
```

---

## 📖 Usage Examples

#### Call an endpoint

```python
from qanswer_sdk import Configuration, ApiClient
from qanswer_sdk.apis import DefaultApi

config = Configuration(host="https://api.qanswer.eu")

with ApiClient(config) as client:
    api = DefaultApi(client)
    result = api.ask_question(question="What is ISO 27001?")
    print(result)
```

#### Handle responses

```python
print(result.answer)      # direct answer
print(result.confidence)  # model confidence
```

---

## ⚙️ Configuration

```python
config = Configuration(
    host="https://api.qanswer.eu",
    api_key={"Authorization": "Bearer <YOUR_TOKEN>"},
    timeout=30
)
```

---

📌 Versioning

This SDK follows the version of the QAnswer API.
The current version is: `3.1186.0 (branch: main)`