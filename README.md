# BankBridge

A banking system featuring a Django REST Framework backend and a C# console client. Supports registration, authentication, deposits, withdrawals, transfers, and transaction history.

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Database Seeding](#database-seeding)
- [Usage Guide](#usage-guide)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [License](#license)

---

## Features

### Backend (Django REST API)

- User registration with automatic account number generation
- Token-based authentication
- Deposit, withdraw, and transfer operations
- Transaction history
- User profile management
- Account balance retrieval
- User search
- CORS support and password hashing

### Frontend (C# Console Client)

- Interactive menu-driven interface
- Token-based authentication flow
- Deposit, withdraw, and transfer operations
- Transaction history display
- Profile management
- Async HTTP communication

---

## Technology Stack

### Backend

| Component | Version |
|-----------|---------|
| Python | 3.8+ |
| Django | 4.2.0 |
| Django REST Framework | 3.14.0 |
| Django CORS Headers | Latest |
| Database | SQLite (default) |

### Frontend

| Component | Details |
|-----------|---------|
| Runtime | .NET 6.0 / 7.0 / 8.0 |
| Language | C# 10.0+ |
| JSON | Newtonsoft.Json |
| HTTP | HttpClient |

---

## Project Structure

```
bankbridge/
├── backend/
│   ├── bankbridge_api/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── api/
│   │   ├── migrations/
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── __init__.py
│   │   │       └── seed_data.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── views.py
│   ├── db.sqlite3
│   ├── manage.py
│   └── requirements.txt
│
└── csharp-client/
    ├── Program.cs
    └── BankBridgeClient.csproj
```

---

## Prerequisites

### Backend

- Python 3.8 or higher
- pip

### Frontend

- .NET SDK 6.0 or higher

---

## Installation and Setup

### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Seed the database:

```bash
python manage.py seed_data
```

6. Start the server:

```bash
python manage.py runserver
```

Backend available at `http://localhost:8000/`.

### Frontend Setup

1. Navigate to the client directory:

```bash
cd csharp-client
```

2. Add the required package:

```bash
dotnet add package Newtonsoft.Json
```

3. Build and run:

```bash
dotnet build
dotnet run
```

---

## Running the Application

### Step 1 - Start the Backend

```bash
cd backend
python manage.py runserver
```

### Step 2 - Run the C# Client

Open a new terminal:

```bash
cd csharp-client
dotnet run
```

---

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/register/` | Register new user | No |
| POST | `/api/login/` | User login | No |
| POST | `/api/logout/` | User logout | Yes |
| GET | `/api/profile/` | Get user profile | Yes |
| PUT | `/api/profile/` | Update user profile | Yes |
| GET | `/api/balance/` | Check balance | Yes |
| POST | `/api/deposit/` | Deposit money | Yes |
| POST | `/api/withdraw/` | Withdraw money | Yes |
| POST | `/api/transfer/` | Transfer money | Yes |
| GET | `/api/transactions/` | Transaction history | Yes |
| GET | `/api/search/` | Search users | Yes |

### Example Requests

Register:

```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","email":"john@example.com","password":"password123","confirm_password":"password123","phone":"1234567890"}'
```

Login:

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"password123"}'
```

Deposit:

```bash
curl -X POST http://localhost:8000/api/deposit/ \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{"amount":500.00}'
```

Transfer:

```bash
curl -X POST http://localhost:8000/api/transfer/ \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{"to_account":"ACC00000002","amount":100.00,"description":"Payment"}'
```

---

## Database Seeding

Running `python manage.py seed_data` clears all existing data and creates fresh records.

### What Gets Created

- 10 predefined users with realistic balances
- 20 randomly generated users
- Sample deposits, withdrawals, and transfers

### Predefined Users

All predefined users share the password `password123`.

| Username | Balance |
|----------|---------|
| john_doe | $5,000.00 |
| jane_smith | $7,500.50 |
| mike_johnson | $3,250.75 |
| sarah_williams | $10,200.00 |
| robert_brown | $2,150.25 |
| emily_davis | $8,900.00 |
| david_miller | $4,320.60 |
| lisa_wilson | $15,750.00 |
| james_moore | $6,100.80 |
| anna_taylor | $9,450.30 |

### Options

```bash
# Default — clears all data, creates 10 predefined + 20 random users
python manage.py seed_data

# Custom number of random users
python manage.py seed_data --random-count 50

# Skip transaction seeding
python manage.py seed_data --skip-transactions
```

---

## Usage Guide

### Main Menu

```
1. Login
2. Register New Account
3. Exit
```

### User Dashboard

```
1. View Profile
2. Check Balance
3. Deposit Money
4. Withdraw Money
5. Send Money
6. Transaction History
7. Logout
```

### Making a Transfer

1. Log in to your account
2. Select "Send Money" from the dashboard
3. Enter the recipient's account number
4. Enter the amount
5. Add an optional description
6. Confirm the transfer

---

## Testing

### cURL

```bash
# Register
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"test123","confirm_password":"test123","phone":"9999999999"}'

# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

# Deposit
curl -X POST http://localhost:8000/api/deposit/ \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{"amount":100.00}'
```

### Python

```python
import requests

# Register
res = requests.post('http://localhost:8000/api/register/', json={
    'username': 'testuser',
    'email': 'test@test.com',
    'password': 'test123',
    'confirm_password': 'test123',
    'phone': '1234567890'
})

# Login
res = requests.post('http://localhost:8000/api/login/',
    json={'username': 'testuser', 'password': 'test123'})
token = res.json()['token']

# Deposit
headers = {'Authorization': f'Token {token}'}
res = requests.post('http://localhost:8000/api/deposit/',
    json={'amount': 500.00}, headers=headers)
print(res.json())
```

---

## Troubleshooting

**Port 8000 already in use**

```bash
python manage.py runserver 8001
```

**C# client cannot connect**

Ensure the Django server is running and `BASE_URL` in `Program.cs` matches the server address. Check that no firewall is blocking port 8000.

**Database migration errors**

```bash
rm db.sqlite3
rm -rf api/migrations/
python manage.py makemigrations api
python manage.py migrate
```

**Missing Python modules**

```bash
pip install djangorestframework django-cors-headers
```

**Authentication token not working**

Log out and log in again to obtain a fresh token. Ensure the `Authorization: Token <token>` header is included on all authenticated requests.

**.NET build errors**

```bash
dotnet --version
dotnet restore
```

---

## Security

- Passwords hashed via Django's built-in hasher
- Token-based stateless authentication
- SQL injection prevented through Django ORM
- CORS configured explicitly
- XSS and CSRF protections enabled by default

### Production Checklist

- Replace `SECRET_KEY` with a secure random value
- Set `DEBUG = False`
- Switch to PostgreSQL or MySQL
- Enforce HTTPS
- Use environment variables for all sensitive configuration
- Add rate limiting to API endpoints

---

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver

# Frontend (new terminal)
cd csharp-client
dotnet restore
dotnet run
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.