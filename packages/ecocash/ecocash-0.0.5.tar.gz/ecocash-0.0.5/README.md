# Ecocash Python Library

Simple, intuitive Python client for Ecocash Open API.

## Installation

```bash
pip install ecocash
```

## Quick Start

```python

from ecocash import Ecocash
wallet = EcoCash(
    app_id="app123", # provided by ecocash in the portal
    api_key="key123", # provided by ecocash in the portal
    merchant_code="850236", # for merchant payments
    app_name="MyApp" # provided by ecocash in the portal
)
```

# Make a payment

this is used to initiate transaction from ***Merchant-Side to Customer-Side** *(customer only has to approve transaction by inputting their pin)

```python
result = wallet.initiate_payment("263774222475", 10.5, "Payment test")
print(result)
```

# Refund example

```python
result = wallet.refund("uuid_here", "012345l61975", "263774222475", 10.5, "Vaya Africa", "USD", "Test refund")p
```

```python
print(result)
```

# Transaction lookup example

```python
result = wallet.check_transaction_status("263774222475", "uuid_here")print(result)
```
