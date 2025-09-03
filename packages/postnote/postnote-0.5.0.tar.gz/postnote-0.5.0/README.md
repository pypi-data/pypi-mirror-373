# postnote

[![PyPI version](https://badge.fury.io/py/postnote.svg)](https://pypi.org/project/postnote/)
[![Python Versions](https://img.shields.io/pypi/pyversions/postnote.svg)](https://pypi.org/project/postnote/)

**postnote** is a lightweight Postman-like client for Jupyter notebooks and Python projects.  
Make HTTP requests inline, preview `curl` commands, and display JSON or [Polars](https://pola.rs/) DataFrames seamlessly.

## ✨ Features
- Simple API for `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- Inline `curl` preview for easy copy/paste
- Pretty Markdown + JSON display inside Jupyter
- Convert list responses directly into Polars DataFrames
- Support for JSON payloads, query params, and multipart file uploads
- Easy auth helpers (`Bearer`, `Basic`)

## 🚀 Installation
```bash
pip install postnote
```

## 📖 Usage

### Basic example
```python
from postnote import Request, RequestSettings

settings = RequestSettings(
    base_url="https://domain.com",
    api_port=443,
    api_version="v1",
    resource_name="users",
    headers={
        "Content-Type": "application/json",
        "X-Client-Key": "your-key",
        "X-Client-Secret": "your-secret",
    },
)

client = Request(settings)

# POST request with JSON payload
payload = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
}
resp = client.post(payload=payload)

# GET request with query params
resp = client.get(params={"page": 1, "limit": 10})
```

### Convert to Polars
If the response contains a list, you can render it directly as a Polars DataFrame:

```python
resp = client.get(params={"page": 1}, to_polars=True)
```

### File upload (multipart/form-data)
```python
files = [("file", open("avatar.png", "rb"))]
resp = client.post(payload={"note": "upload"}, files=files, endpoint="upload")
```

### Quick auth
```python
client.set_bearer("your_token_here")
# or
client.set_basic("username", "password")
```

## 🔧 Development
Clone the repo and install in editable mode:

```bash
git clone https://github.com/daviguides/postnote.git
cd postnote
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```


## 📜 License
MIT License © 2025 [Davi Guides](https://github.com/daviguides)
