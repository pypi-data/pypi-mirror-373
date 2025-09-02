# stigg-api-client

This library provides a Python wrapper to [Stigg's GraphQL API](https://docs.stigg.io/docs/graphql-api) based on 
the operations that are in use by the [Stigg's Node.js SDK](https://docs.stigg.io/docs/nodejs-sdk).

It leverages the [sgqlc](https://github.com/profusion/sgqlc) library to generate Python classes for GraphQL types, and
utilizes the `sgqlc.endpoint.requests.RequestsEndpoint` class to send the API requests. The responses are being
automatically converted into native Python types.

## Documentation

See https://docs.stigg.io/docs/python-sdk

## Installation

    pip install stigg-api-client

## Usage

Initialize the client:

```python

import os
from stigg import Stigg

api_key = os.environ.get("STIGG_SERVER_API_KEY")

stigg_client = Stigg.create_client(api_key)

```

Provision a customer

```python

import os
from stigg import Stigg

api_key = os.environ.get("STIGG_SERVER_API_KEY")

client = Stigg.create_client(api_key)

data = client.request(Stigg.mutation.provision_customer, {
    "input": {
        "refId": "customer-id",
        "name": "Acme",
        "email": "hello@acme.com",
        "couponRefId": "coupon-id",
        "billingInformation": {
            "language": "en",
            "timezone": "America/New_York",
            "billingAddress": {
                "country": "US",
                "city": "New York",
                "state": "NY",
                "addressLine1": "123 Main Street",
                "addressLine2": "Apt. 1",
                "phoneNumber": "+1 212-499-5321",
                "postalCode": "10164"
            },
            "shippingAddress": {
                "country": "US",
                "city": "New York",
                "state": "NY",
                "addressLine1": "123 Main Street",
                "addressLine2": "Apt. 1",
                "phoneNumber": "+1 212-499-5321",
                "postalCode": "10164"
            }
        },
        "additionalMetaData": {
            "key": "value"
        },
        "subscriptionParams": {
            "planId": "plan-revvenu-basic"
        }
    }
})

print(data.provision_customer.customer.name)

```

Get a customer by ID

```python

import os
from stigg import Stigg

api_key = os.environ.get("STIGG_SERVER_API_KEY")

client = Stigg.create_client(api_key)

data = client.request(Stigg.query.get_customer_by_id, {
  "input": {"customerId": "customer-id"}
})

customer = data.get_customer_by_ref_id
print(customer.name)

```
