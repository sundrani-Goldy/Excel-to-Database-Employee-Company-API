# Excel Import Project

This project is a Django-based API that reads data from an Excel or CSV file and inserts it into a database. The project is structured to follow Django best practices and is containerized using Docker.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Running the Project](#running-the-project)

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python](https://www.python.org/downloads/) (if not using Docker for development)

## Setup Instructions

Follow these steps to set up the project:

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd excel_import_project
   ```

2. **Create a Virtual Environment (Optional):**
   If you are not using Docker for development, create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install Dependencies:**
   If you are using Docker, this step will be handled in the Dockerfile. If not, install the dependencies locally:
   ```bash
   pip install -r requirements.txt
   ```
   NOTE: USing python3.13.2 

4. **Build the Docker Container:**
   If using Docker, build the container:
   ```bash
   docker-compose build
   ```

5. **Run Migrations:**
   This step sets up the database tables:
   ```bash
   docker-compose run web python manage.py makemigrations
   docker-compose run web python manage.py migrate
   ```

## Running the Project

To start the server, run the following command:
```bash
docker-compose up
```

The API will be available at `http://localhost:8000`.