# Excel Import Project

This project is a Django-based API that reads data from an Excel or CSV file and inserts it into a database. It provides functionality to manage employee and company data through a RESTful API interface.

## Features

- Import employee and company data from Excel (.xlsx) or CSV files
- Automatic company creation if not exists
- Duplicate employee detection
- Data validation and error handling
- RESTful API endpoints for data access
- Swagger documentation interface

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Running the Project](#running-the-project)
- [API Documentation](#api-documentation)
- [API Endpoints](#api-endpoints)
- [Data Format](#data-format)

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python](https://www.python.org/downloads/) (if not using Docker for development)

## Setup Instructions

Follow these steps to set up the project:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/sundrani-Goldy/Excel-to-Database-Employee-Company-API.git
   ```

2. **Navigate to Project Directory:**
   ```bash
   cd Excel-to-Database-Employee-Company-API
   ```

3. **Set up Environment Variables:**
   ```bash
   # For Linux/Mac
   cp .env.example .env
   
   # For Windows
   copy .env.example .env
   ```

4. **Build the Docker Container:**
   ```bash
   docker compose build
   ```

## Running the Project

1. **Start the Server:**
   ```bash
   docker compose up
   ```

2. **Run Migrations:**
   ```bash
   docker compose run web python manage.py makemigrations
   docker compose run web python manage.py migrate
   ```

## API Documentation

Once the server is running, you can access the API documentation and interactive interface at:
- Swagger UI: `http://localhost:8000/swagger`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

The following endpoints are available:

- `POST /api/upload/`: Upload Excel/CSV file for data import
- `GET /api/companies/`: List all companies
- `GET /api/employees/`: List all employees

## Data Format

The Excel/CSV file must contain the following columns:

- `COMPANY_NAME`: Name of the company
- `FIRST_NAME`: Employee's first name
- `LAST_NAME`: Employee's last name
- `PHONE_NUMBER`: Employee's phone number
- `EMPLOYEE_ID`: Unique identifier for the employee
- `MANAGER_ID`: ID of the employee's manager
- `DEPARTMENT_ID`: ID of the employee's department
- `SALARY`: Employee's salary

### Validation Rules

- File size must not exceed 10MB
- Supported formats: .xlsx and .csv
- Employee ID must be unique within a company
- Salary must be a positive number
- All required columns must be present

### Response Format

The API returns detailed responses including:
- Success/failure status
- Number of companies and employees processed
- Validation errors if any
- Duplicate entries if found
- Detailed error messages for troubleshooting

## Error Handling

The system provides comprehensive error handling for:
- Invalid file formats
- Missing required columns
- Data validation errors
- Duplicate entries
- File processing errors