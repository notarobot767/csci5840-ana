FROM python:3.14

ENV TZ="Etc/UTC"

WORKDIR /app

COPY ./requirements.txt ./

# 1. Install system utilities + SSH binaries needed by Ansible & network CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
        iputils-ping \
        openssh-client \
        sshpass \
        libssh-dev \
        libssl-dev \
        gcc \
        python3-dev \
        build-essential && \
    \
    # 2. Install Python dependencies
    pip3 install --upgrade pip setuptools wheel --no-cache-dir && \
    pip3 install --no-cache-dir -r ./requirements.txt && \
    \
    # 3. Pre-install Ansible Collections for your devices
    ansible-galaxy collection install --no-cache \
        ansible.netcommon \
        cisco.ios \
        arista.eos \
        napalm.napalm && \
    \
    # 4. Cleanup apt cache
    rm -rf /var/lib/apt/lists/*

COPY ./docker-entrypoint.sh /etc/
RUN chmod +x /etc/docker-entrypoint.sh

# Run app with gunicorn backend
EXPOSE 5000
ENTRYPOINT [ "/etc/docker-entrypoint.sh" ]
CMD [ "--workers", "4", "--bind", "0.0.0.0:8080", "wsgi:app"]