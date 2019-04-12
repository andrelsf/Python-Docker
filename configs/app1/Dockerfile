FROM	centos:latest

LABEL	app1.version="1.0" \
	app1.vendor="Andre L S Ferreira" \
	app1.description="Chellenge 4Linux App 1."

RUN	yum makecache fast \
	&& yum install epel-release -y \
	&& yum install httpd httpd-tools -y

RUN	echo "<html><body><br><center><h1>Welcome to APP1.</h1></center></body></html>" > /var/www/html/index.html
RUN	chown root:apache /var/www/ -R

CMD	["/usr/sbin/apachectl", "-D", "FOREGROUND"]