# Use the official Python image from Docker Hub
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app
COPY . .

# Expose the port your app will run on
EXPOSE 5000

# Define the command to run the app
CMD ["python", "app.py"]
