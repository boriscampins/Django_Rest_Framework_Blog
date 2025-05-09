FROM python:3.9

# install ssw client
RUN apt-get update && apt-get install -y openssh-client


# Set enviroment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy requirements.txt file
COPY requirements.txt /app/requirements.txt

# Install python dependencies
RUN pip install -r requirements.txt

# Copy the aplication to the working directory
COPY . /app/

# Start SSH tunnel
CMD python manage.py runserver 0.0.0.0:8000
