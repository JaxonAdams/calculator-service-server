# "Premium Calculator" Server

# Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [API Documentation](#api-documentation)
4. [Setup](#setup)
5. [Running the Service Locally](#running-the-service-locally)
6. [Running Tests](#running-tests)
7. [Deployment](#deployment)

## Project Overview

This project is a calculator service that performs various operations and provides an API for accessing these operations. The service is built using Flask and integrates with a MySQL database.

The calculator uses a transaction-based system wherin a user starts with a certain balance, and requesting operations decreases that balance.

This repository hosts the server side of the project. You can find the client side [here](https://github.com/JaxonAdams/calculator-service-client).

## Prerequisites

 - Python 3.12
 - MySQL
 - Node.js and npm (for Serverless framework)

## API Documentation

Base URL: `https://khbna0u3ti.execute-api.us-west-1.amazonaws.com/dev/api/v1`

### Authentication

#### `/auth/login`

Request a user JWT from the server. Requires the following fields in a JSON payload:
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

## Running Tests
To run the tests, use `pytest`:
```bash
$ pytest
```

## Deployment
This project uses the Serverless Framework for deployment. To deploy the service to AWS, run the following:
```bash
$ serverless deploy
```