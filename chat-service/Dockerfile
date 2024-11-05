# # Use Python 3.9 as the base image
# FROM python:3.9-slim

# # Set the working directory inside the container
# WORKDIR /LLMAPP

# # Copy the requirements file and install dependencies
# COPY requirements.txt /LLMAPP/
# RUN pip3 install --no-cache-dir -r requirements.txt

# # Copy the rest of the application code into the container
# COPY . /LLMAPP/

# # Expose the correct port (5005) that the Flask app will run on
# EXPOSE 5004

# # Set the entry point to run the Flask app
# CMD ["python3", "main.py"]


# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /LLMAPP

# Copy the requirements file and install dependencies
COPY requirements.txt /LLMAPP/
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip3 install gunicorn

# Copy the rest of the application code into the container
COPY . /LLMAPP/

# Expose the correct port (5004) that the Flask app will run on
EXPOSE 5004

# Set the entry point to run the Flask app with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5004", "main:app"]
