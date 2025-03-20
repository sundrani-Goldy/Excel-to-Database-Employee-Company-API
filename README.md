# Excel Import Project

This project is a Django-based API that reads data from an Excel or CSV file and inserts it into a database.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Running the Project](#running-the-project)
- [API Documentation](#api-documentation)

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
   # Replace 'Excel-to-Database-Employee-Company-API' with your actual project directory name
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