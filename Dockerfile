# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install timezone data
RUN apt-get update && apt-get install -y tzdata

# Set the timezone to Vienna
ENV TZ=Europe/Vienna

RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the script when the container launches
CMD ["python", "./notion_prayer.py"]
