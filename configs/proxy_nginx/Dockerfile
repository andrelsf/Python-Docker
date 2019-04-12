FROM	ubuntu:latest

LABEL	proxy_nginx.version="1.0" \
	    proxy_nginx.vendor="Andre L S Ferreira" \
	    proxy_nginx.description="MeetUP DevOPs."

RUN     apt update \
        apt install nginx -y \
        rm -f /etc/nginx/sites-enabled/default

ADD    ./vhost_app1 /etc/nginx/conf.d/
ADD    ./vhost_app2 /etc/nginx/conf.d/


CMD	    ["/etc/init.d/nginx", "start"]