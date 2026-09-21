FROM nginx:1.29
# https://hub.docker.com/_/nginx

ENV TZ=Etc/UTC
# set timezone variable to UTC
# set actual timezone with TZ ENV variable in compose file
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

RUN rm -rf /usr/share/nginx/html/*
# remove default.conf

COPY ./app/docker-entrypoint.sh /etc/
RUN chmod +x /etc/docker-entrypoint.sh
# copy entrypoint file
# add execution permission to script

ENTRYPOINT ["/etc/docker-entrypoint.sh"]
# use entrypoint to set timezone and other settings
# also allow for command injection in compose file
# http://nginx.org/en/docs/switches.html

CMD ["-g", "daemon off;"]
# http://nginx.org/en/docs/switches.html

EXPOSE 80/tcp
# default port for web service

COPY ./app/nginx/. /etc/nginx/