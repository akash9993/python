# Use official Python base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

COPY profile.json /app/profile.json

# Install dependencies
# RUN pip install --no-cache-dir flask pandas delta-sharing pandasql requests

RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Command to run the application
CMD ["python", "flaskapi.py"]
