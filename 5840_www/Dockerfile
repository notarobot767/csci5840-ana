FROM python:3.14 AS builder

ENV TZ="Etc/UTC"
# set timezone variable to UTC
# set actual timezone with TZ ENV variable in compose file
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
#
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt
ENTRYPOINT [ "/etc/docker-entrypoint.sh" ]

# www main web app using gunicorn
#################################
FROM builder AS www

COPY ./docker-entrypoint-www.sh /etc/docker-entrypoint.sh
RUN chmod +x /etc/docker-entrypoint.sh

# www main web app using gunicorn
#################################
FROM builder AS webtest

COPY ./docker-entrypoint-webtest.sh /etc/docker-entrypoint.sh
RUN chmod +x /etc/docker-entrypoint.sh

EXPOSE 5000
CMD [ "app.py" ]