# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Get port from build args (default: 80)
ARG PORT=80

# Set the working directory in the container
WORKDIR /app

# install build-essentials for fasttext
RUN apt-get update && apt-get install -y build-essential wget curl

# Install any needed packages specified in requirements.txt
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --default-timeout=6000 --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY app /app

# Make port available to the world outside this container
EXPOSE $PORT

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run uvicorn server
ENV PORT=$PORT
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT
