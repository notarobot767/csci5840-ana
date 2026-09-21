# Visual Studio Code

Provides an [IDE](https://en.wikipedia.org/wiki/Integrated_development_environment) code editor with syntax highlighting and autocomplete in a web browser. You should use this web app or a stand alone version of VS Code on your management computer to edit the docker configurations.

| Docker Images | Tag |
|-|-|
| [code](https://hub.docker.com/r/linuxserver/code-server) | latest |

## Components
This is a single container application. It's simple and pulls from the cod-server image from linuxserver.io.

## References
- [Linux Server](https://www.linuxserver.io/)
- [Visual Studio Code](https://code.visualstudio.com/)

## Prerequisites
- Linux OS
- [Docker Compose](https://docs.docker.com/engine/install/)

## Getting Started
Review the project's [compose.yml](https://web.git.mil/tss/code/-/blob/main/compose.yml) file and Docker Compose CLI in references.

### Download Project to your Linux host or VM
Clone the project using git or another means to a folder called code. It's recommended to add a prefix like prod or test to the folder name as that will ensure the container and network will be named with it. For example:

$ `git clone https://sync.git.mil/tss/code.git prod_code`

### [Publishing and Exposing Ports](https://docs.docker.com/get-started/docker-concepts/running-containers/publishing-ports/)
In the [compose.yml](https://web.git.mil/tss/guac/-/blob/main/compose.yml) file, configure the ports section for the guac service. By default the container listens on http port 8443, but you can map any unused port on the host OS to the container. The mapping should follow the format Host "IP:Host Port:Container Port".

```
code:
  ports:
    - 192.168.0.1:80:8443
```

### Pull the Docker Images
$ `docker compose pull`

### Run the Stack
$ `docker compose up -d`

### Checking for Syslog Errors
See if any blatant errors appear in the syslog

$ `docker compose logs -f --tail 20`

### Connect to Web GUI
From your client web browser on a management computer, attempt to connect. In our example, we would connect to the IP and port we specified in the ports section of compose.yml:

`http://192.168.0.1:80/guacamole`

### Connect Codeserver to Nginx Proxy
Review the README.md in the [Nginx Proxy](https://web.git.mil/tss/proxy) for additional guidance.

#### Rebind Codeserver for the Proxy
By default, Codeserver should bind to the proxy bridge 172.31.255.255 on port 7000. So you should configure the ports section in compose.yml to mirror:

```
code:
  ports:
    - 172.31.255.255:7005:8080
```

Be cause we modified the compose.yml, we will need to recreate the Codeserver container.

$ `docker compose up -d`

#### Check the Virtual Listener
Change the Codeserver virtual listener, [code.conf](https://web.git.mil/tss/proxy/-/blob/main/app/local_proxy_conf/auth_proxy/conf.d/code.conf), to direct to use your specified domain. This should include all of the return and proxy_pass statements.

```
server {
  listen 80;
  server_name code;
  server_name code.tss.usar.army.mil;
  return 301 https://code.tss.usar.army.mil;
}

server {
  listen 443 ssl;
  http2 on;
  server_name code;
  return 301 https://code.tss.usar.army.mil;
}

server {
  listen 443 ssl;
  http2 on;
  server_name code.tss.usar.army.mil;
  
  location / {
    proxy_pass http://${PROXY_BRIDGE}:${CODE_PORT};
    #include /etc/nginx/custom_confs/authentik_root.conf;
  }

  #include /etc/nginx/custom_confs/authentik.conf;
}

```

Changes to the virtual listener will require a rebuild of the proxy. In this case, we are only modifying the authentication proxy, so we only need to rebuild that image and recreate that container.

$ `docker compose build auth_proxy`

$ `docker compose up -d auth_proxy`

#### Connect to Web GUI via Proxy
This virtual listener is expecting the domain `code.tss.usar.army.mil`. You will need to either create a local DNS record or edit your management computer's hosts file. If you don't have a DNS server, recommend using [Pi-hole](https://web.git.mil/tss/pihole) which is included in the TSS. Since Guacamole is considered a critical app for management, you should point its DNS record to the authentication proxy.

In your web browser of your management computer, connect to Codeserver. For our example, this would be:

`https://code.tss.usar.army.mil`