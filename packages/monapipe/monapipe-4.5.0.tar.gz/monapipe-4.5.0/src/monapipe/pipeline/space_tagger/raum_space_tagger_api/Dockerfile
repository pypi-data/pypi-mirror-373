# Use an official Python runtime as a parent image
FROM python:3.9

# Get port from build args (default: 80)
ARG PORT=80

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libffi-dev \
    libssl-dev \
    libblas-dev \
    liblapack-dev \
    gfortran \
    curl \
    wget \
    && apt-get clean

# Install OpenJDK 11 for the appropriate architecture
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        echo "Downloading OpenJDK for x86_64..."; \
        wget https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.19%2B7/OpenJDK11U-jdk_x64_linux_hotspot_11.0.19_7.tar.gz -O /tmp/openjdk.tar.gz; \
    elif [ "$ARCH" = "aarch64" ]; then \
        echo "Downloading OpenJDK for ARM64..."; \
        wget https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.19%2B7/OpenJDK11U-jdk_aarch64_linux_hotspot_11.0.19_7.tar.gz -O /tmp/openjdk.tar.gz; \
    else \
        echo "Unsupported architecture: $ARCH"; \
        exit 1; \
    fi && \
    mkdir -p /usr/lib/jvm/java-11-openjdk && \
    tar -xvzf /tmp/openjdk.tar.gz -C /usr/lib/jvm/java-11-openjdk --strip-components=1 && \
    rm /tmp/openjdk.tar.gz

# Set JAVA_HOME for Java 11
ENV JAVA_HOME="/usr/lib/jvm/java-11-openjdk"
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install Rust and Cargo
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --default-timeout=12000 --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY app /app

# Make port available to the world outside this container
EXPOSE $PORT

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run uvicorn server
ENV PORT=$PORT
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT
