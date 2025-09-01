# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

# Use an official Pytorch runtime as a parent image
FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-runtime

# Get port from build args (default: 80)
ARG PORT=80

# Set the working directory in the container
WORKDIR /app

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
