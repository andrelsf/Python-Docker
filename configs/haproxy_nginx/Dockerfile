FROM	haproxy:1.9

LABEL	HAProxy.vendor="Andre L S Ferreira" \
		HAProxy.description="MeetUP DevOPs 2."

ADD ./haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg

RUN	useradd haproxy \
	&& chown haproxy. /usr/local/etc/haproxy/ -R

CMD ["/usr/local/sbin/haproxy", "-f", "/usr/local/etc/haproxy/haproxy.cfg"]