FROM telegraf:latest

USER root

# Install Python 3, pip, and required system build deps for ncclient/cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install ncclient and xmltodict
RUN pip3 install --no-cache-dir --break-system-packages ncclient xmltodict

# Copy the poller script into the container
COPY poll_netconf.py /usr/local/bin/poll_netconf.py
RUN chmod +x /usr/local/bin/poll_netconf.py

USER telegraf