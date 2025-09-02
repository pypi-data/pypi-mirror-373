# Vayu API Client Library [![PyPI Latest Version](https://img.shields.io/pypi/v/vayu-py.svg)](https://pypi.org/project/vayu-py/)

## Overview

The Vayu API client library in Python allows you to submit events for processing and storage, manage billing-related entities, and perform various other operations seamlessly.

## Installation

Install the Vayu API client library using pip:

```bash
pip install vayu-py
```

## Usage

### Initialization

Initialize the Vayu API client. The `base_url` parameter is optional and defaults to Vayu's public API servers.

```python
from vayu_sdk import Vayu

vayu = Vayu(
    api_key='your-api-token',
    host='https://connect.withvayu.com'  # Optional
)
```

### Authentication

#### Login and authenticate

```python
response = vayu.login()
```

### Events

#### Sending Events

To send a batch of events for processing and storage:

```python
events = [
    Event(
      name='api_call',
      ref='4f6cf35x-2c4y-483z-a0a9-158621f77a21',
      timestamp=datetime.strptime('2023-09-13T18:25:43.511Z', '%Y-%m-%dT%H:%M:%S.%fZ'),
      customerAlias='customer_12345',
      data={
            'key1': 'processing_duration',
            'key2': 'api_url'
        }
    )
]

response = vayu.events.send(events=events)

print(response['valid_events'])
print(response['invalid_events'])
```

#### Querying Events

To fetch events occurring within a specified timestamp range:

```python
response = vayu.events.query(
  start_time=datetime.strptime('2023-09-01T00:00:00.000Z', '%Y-%m-%dT%H:%M:%S.%fZ'),
  end_time=datetime.strptime('2023-09-30T23:59:59.999Z', '%Y-%m-%dT%H:%M:%S.%fZ'),
  event_name='api_call',
  limit=10
)

print(response['events'])
```

#### Getting Event by Ref ID

To get a specific event using its reference ID:

```python
response = vayu.events.get(ref='4f6cf35x-2c4y-483z-a0a9-158621f77a21')

print(response['event'])
```

#### Deleting Event by Ref ID

To delete a specific event using its reference ID:

```python
response = vayu.events.delete(ref='4f6cf35x-2c4y-483z-a0a9-158621f77a21')

print(response['event'])
```

### Customers

#### Creating a Customer

To create a new customer:

```python
response = vayu.customers.create(
  name='John Doe',
  external_id='customer_12345'
)

print(response['customer'])
```

#### Updating a Customer

To update an existing customer by ID:

```python
response = vayu.customers.update(
  id='customer-id',
  external_id='customer_67890'
)

print(response['customer'])
```

#### Deleting a Customer

To delete a customer by ID:

```python
response = vayu.customers.delete(id='customer-id')

print(response['customer'])
```

### Contracts

#### Assigning a contract to a customer

In order to assign a contract to a customer you would need to provide the customer Id and the relevant plan

```python
response = vayu.contracts.create(
  start_date=time.time(), 
  end_date=None, 
  customer_id='1f4cf23x-2c4y-483z-1111-158621f77a21', 
  plan_id='4f6cf35x-1234-483z-a0a9-158621f77a21'
)

print(response['contract'])
```

### Meters

Meters are entities that track and aggregate usage data based on events. They are crucial for billing and monitoring purposes. Each meter is associated with a specific event name and has an aggregation method to sum up usage values.

#### Getting a Meter by ID

To get a meter by ID:

```python
response = vayu.meters.get(id='meter-id')

print(response['meter'])
```

#### Updating a Meter

To update a meter by ID:

```python
response = vayu.meters.update(
  id='meter-id',
  name='Updated Meter Name',
  event_name='api_call',
  aggregation_method= AggregationMethod(
    field='usage',
    operator=AggregationOperator.SUM
  ),
  filter=Filter(
    conditions=[
      Condition(criterions=[
        Criterion(
          field='event',
          operator=CriterionOperator.EQUALS,
          value='api_call'
        )
      ])
    ]
  )
)

print(response['meter'])
```

#### Deleting a Meter

To delete a meter by ID:

```python
response = vayu.meters.delete(id='meter-id')

print(response['meter'])
```

## Features

The Vayu API client library provides access to the following features:

- **Auth**
  - `login()`
- **Events**
  - `events.get()`
  - `events.delete()`
  - `events.query()`
  - `events.send()`
  - `events.dry_run()`
- **Customers**
  - `customers.list()`
  - `customers.get()`
  - `customers.getByExternalId()`
  - `customers.create()`
  - `customers.update()`
  - `customers.delete()`
- **Meters**
  - `meters.get()`
  - `meters.update()`
  - `meters.delete()`
  - `meters.list()`
- **Plans**
  - `plans.list()`
  - `plans.get()`
  - `plans.delete()`
- **Contracts**
  - `contracts.list()`
  - `contracts.get()`
  - `contracts.create()`
  - `contracts.delete()`
- **Invoices**
  - `invoices.list()`
  - `invoices.get()`

## Support

If you have any questions or need further assistance, please contact Vayu at `team@withvayu.com`.

## License

This project is licensed under the MIT License.

---

This README provides an overview and usage examples for the Vayu API client library. For more detailed information on each method, please refer to the official Vayu API documentation.