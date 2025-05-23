# Use official Python base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5001
EXPOSE 5001

# Command to run the application
CMD ["python", "flaskapi.py"]
