FROM python:3.14 AS builder

ENV TZ="Etc/UTC"
# set timezone variable to UTC
# set actual timezone with TZ ENV variable in compose file
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

ENV PYTHONUNBUFFERED=1

RUN pip3 install --no-cache-dir --upgrade pip
ENTRYPOINT [ "/etc/docker-entrypoint.sh" ]
WORKDIR /app

FROM builder AS make_ansible_play
COPY ./docker-entrypoint.make_ansible_play.sh /etc/docker-entrypoint.sh
COPY ./requirements_make_ansible_play.txt ./requirements.txt
RUN chmod +x /etc/docker-entrypoint.sh && \
    pip3 install --no-cache-dir -r ./requirements.txt
CMD ["make_ansible_play.py"]

FROM builder AS make_device_config
COPY ./docker-entrypoint.make_device_config.sh /etc/docker-entrypoint.sh
COPY ./requirements_make_router_config.txt ./requirements.txt
RUN chmod +x /etc/docker-entrypoint.sh && \
    pip3 install --no-cache-dir --upgrade -r ./requirements.txt
CMD ["site.yaml"]