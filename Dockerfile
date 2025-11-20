# Base image
FROM debian:bullseye-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies: build tools for C, Python, curl/git for rustup
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3 \
    python3-pip \
    ca-certificates \
    curl \
    git \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain (rustup installs rustc and cargo)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . /root/.cargo/env \
    && rustup default stable
ENV PATH="/root/.cargo/bin:${PATH}"

# Create app dir and copy files early to leverage Docker cache
WORKDIR /app
COPY . /app

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Expose Streamlit port and listen on all interfaces
EXPOSE 8501

# Default command: run Streamlit on 0.0.0.0 so it's reachable from host
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
