FROM	haproxy:1.7

LABEL	HAProxy.vendor="Andre L S Ferreira" \
		HAProxy.description="MeetUP DevOPs 2."

RUN apt update\
	&& apt install haproxy vim net-tools iputils-ping -y \
	&& echo "ENABLED=1" > /etc/default/haproxy