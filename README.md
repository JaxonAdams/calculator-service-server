# "Premium Calculator" Server

# Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [API Documentation](#api-documentation)
4. [Setup](#setup)
5. [Running the Service Locally](#running-the-service-locally)
6. [Running Tests](#running-tests)
7. [Deployment](#deployment)

-----

## Project Overview

This project is a calculator service that performs various operations and provides an API for accessing these operations. The service is built using Flask and integrates with a MySQL database.

The calculator uses a transaction-based system wherin a user starts with a certain balance, and requesting operations decreases that balance.

This repository hosts the server side of the project. You can find the client side [here](https://github.com/JaxonAdams/calculator-service-client).

-----

## Prerequisites

 - Python 3.12
 - MySQL
 - Node.js and npm (for Serverless framework)

-----

## API Documentation

Base URL: `https://khbna0u3ti.execute-api.us-west-1.amazonaws.com/dev/api/v1`
Required headers:
```
Authorization: Bearer <token>
```

Note that `Authorization` is not required when sending a request to `POST /auth/login`.

All routes, except when stated otherwise, require a "user" token generated from a login request.

Some routes require administrator permissions with an "admin" token. Reach out to Jaxon Adams if you need an administrator token for testing purposes.

### Authentication API

#### `POST /auth/login`

Retrieve a user JWT from the server. Requires the following fields in a JSON payload:
```JSON
{
    "username": "<your-username>",
    "password": "<your-secret-password>"
}
```

Status codes:
 - `200` - Success
 - `401` - Invalid password
 - `404` - User not found

Fields included in the response:
 - `token` - Your user JWT for API access. Valid for 1 hour.

### Calculation API

#### `GET /calculation`

Retrieve your calculation history. This endpoint supports filtering by operation type, start date, and end date. It also supports pagination with 'page' and 'page_size' query parameters.

Sample request:
`GET /calculation?type=multiplication&start_date=2024-11-11&page=2&page_size=5`

The above URL requests the second page of your calculation history for all "multiplication" operations on or after November 11, 2024. It specifies a page size of 5 records per-page.

Status codes:
 - `200` - Success
 - `400` - Client-error -- check your query string

Sample response:
```JSON
{
  "metadata": {
    "page": 1,
    "page_size": 2,
    "total": 26
  },
  "results": [
    {
      "calculation": {
        "operands": [
          -6,
          128
        ],
        "operation": "multiplication",
        "result": -768
      },
      "date": "2024-11-13 11:19:53",
      "id": 31,
      "operation": {
        "cost": "0.25",
        "id": 3,
        "type": "multiplication"
      },
      "user": {
        "id": 1,
        "status": "active",
        "username": "test.user@example.com"
      },
      "user_balance": "13.50"
    },
    {
      "calculation": {
        "operands": [
          144
        ],
        "operation": "square_root",
        "result": 12.0
      },
      "date": "2024-11-13 11:15:30",
      "id": 30,
      "operation": {
        "cost": "0.75",
        "id": 5,
        "type": "square_root"
      },
      "user": {
        "id": 1,
        "status": "active",
        "username": "test.user@example.com"
      },
      "user_balance": "13.75"
    }
  ]
}
```

#### `POST /calculation/new`

Request a new calculation from the server. For more information on available operations and their required operand settings, send a request to `GET /operations`.

Required fields:
 - `operation` - The type of operation you're requesting, for example, "square_root"
 - `operands` - The operands you'd like used in the operation. Note that for some calculations like "random_string", your operands will be an array with a single object. The object would hold the settings for the operation. Other operations like "addition" require an array of numbers.

Sample request:
```JSON
{
    "operation": "subtraction",
    "operands": [17, 6, -2]
}
```

Status codes:
 - `200` - Calculation ran successfully
 - `400` - Invalid request -- check your request body
 - `402` - Insufficient funds -- you're out of money!

Sample response:
```JSON
{
    "operands": [
        17,
        6,
        -2
    ],
    "operation": "subtraction",
    "result": 13
}
```

#### `DELETE /calculation/<record_id>`

Delete a calculation record by ID, removing it from the user's history and increasing the user's balance.

This route is not available to an ordinary user -- you need an administrator API key.

Status codes:
 - `200` - The calculation record was successfully deleted.
 - `404` - The calculation with the provided ID could not be found.

-----

## Setup

Follow these steps to get the server up and running on your local computer.

1. Clone the repository:
```bash
$ git clone https://github.com/JaxonAdams/calculator-service-server.git
$ cd calculator-service-server
```

2. Create a virtual environment and activate it:
```bash
$ python -m venv .venv
$ source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

3. Install the required Python packages:
```bash
$ pip install -r requirements.txt
```

4. Install the required Node.js packages:
```bash
$ npm install
```

5. Set up the MySQL database:
```bash
$ mysql -u <username> -p < calculator_service < sql/schema.sql
```

6. [Optional] Create a new entry in the `user` table, then seed the database:
```bash
$ mysql -u <username> -p < calculator_service < sql/seed.sql
```

7. Set environment variables:
The following variables need to be set:
```
JWT_SECRET=<your-jwt-secret>
DB_HOST=<your-db-host>
DB_USER=<your-db-user>
DB_PASSWORD=<your-db-password>
```

-----

## Running the Service Locally
1. Start the Flask application:
The service will be available at `http://127.0.0.1:5000`.
```bash
$ flask run
```
2. Test the Calculator Service:
If you want to test the calculations without running a server, you can run the `calculator_service.py` file:
```bash
$ python services/calculator_service.py
```

-----

## Running Tests
To run the tests, use `pytest`:
```bash
$ pytest
```

-----

## Deployment
This project uses the Serverless Framework for deployment. To deploy the service to AWS, run the following:
```bash
$ serverless deploy
```