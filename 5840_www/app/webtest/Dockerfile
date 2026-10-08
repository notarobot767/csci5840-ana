FROM python:3.14

ENV TZ="Etc/UTC"
# set timezone variable to UTC
# set actual timezone with TZ ENV variable in compose file
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

WORKDIR /app

COPY ./requirements.txt ./

# Install iputils-ping (provides ping and ping6)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # install utils
        iputils-ping && \
    \
    # install python requirements
    pip install --no-cache-dir -r ./requirements.txt && \
    \
    # remove cache
    rm -rf /var/lib/apt/lists/*
    
COPY ./docker-entrypoint.sh /etc/
RUN chmod +x /etc/docker-entrypoint.sh

# run app solely with flask
EXPOSE 8080
ENTRYPOINT [ "/etc/docker-entrypoint.sh" ]
CMD [ "app.py" ]