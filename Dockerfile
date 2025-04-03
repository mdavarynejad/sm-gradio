FROM ubuntu:22.04

# Prevent tzdata interactive prompt
ENV TZ=Etc/UTC
ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies, including Git and tzdata, add deadsnakes PPA
RUN apt-get update && apt-get install -y \
    apt-utils \
    git \
    software-properties-common \
    tzdata \
    && ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update \
    && rm -rf /var/lib/apt/lists/*

# Install the latest Python (e.g., Python 3.11) and required tools
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-distutils \
    python3-pip \
    && ln -s /usr/bin/python3.11 /usr/bin/python \
    && python -m pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /workspace
COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7862

CMD [ "python", "trader.py" ]