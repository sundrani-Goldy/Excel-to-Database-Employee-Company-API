# pull the official base image
FROM python:3.11

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update

RUN pip install --upgrade pip

COPY ./requirements.txt /app/
RUN pip install -r requirements.txt
RUN touch /var/container_initialized

# copy project
COPY . /app/

# Make entrypoint script executable
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]