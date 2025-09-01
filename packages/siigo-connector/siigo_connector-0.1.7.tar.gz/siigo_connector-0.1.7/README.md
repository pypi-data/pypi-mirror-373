# siigo_connector — Python client for the Siigo API

> [!WARNING]
> **Status:** Under development (alpha). Breaking changes may occur.

A small, typed client for [Siigo](https://api.siigo.com). It handles auth (JWT with `username` + `access_key` + `Partner-Id`), retries, and pagination so you can call Python methods instead of crafting HTTP requests.

> Requires Python 3.9+

## Install

Create and activate a virtual environment and then install FastAPI:

```bash
pip install siigo-connector
```

## Usage

Create the Client instance

```python
from src.siigo_connector import client as siigo

c = siigo.Client(
    username="siigoapi@pruebas.com",
    access_key="<access_token>",
    partner_id="myapp",  # short, no spaces
)
```

### Customers

```python
for cust in c.customers.list(created_start="2024-08-30"):
    print(cust)
```

Close the connection after at the end

```python
c.close()
```
