
# Ecocash Python Library

Simple, intuitive Python client for Ecocash Open API.

## Installation

```bash
pip install ecocash
```

## Quick Start

```python

from ecocash import Ecocashec = EcoCash(
    app_id="app123",
    api_key="key123",
    merchant_code="850236",
    app_name="MyApp"
)
```


# Make a payment

```python
result = ec.payment("263774222475", 10.5, "Payment test")
print(result)
```

# Refund example

```python
result = ec.refund("uuid_here", "012345l61975", "263774222475", 10.5, "Vaya Africa", "USD", "Test refund")p
```

```python
print(result)
```

# Transaction lookup example

```python
result = ec.transaction_status("263774222475", "uuid_here")print(result)
```
