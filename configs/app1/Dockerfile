FROM	centos:latest

LABEL	app1.vendor="Andre L S Ferreira" \
		app1.description="MeetUP DevOPs 2."

RUN		yum makecache fast \
		&& yum install epel-release -y \
		&& yum install httpd httpd-tools -y

RUN		echo "<html><body><br><center><h1>Welcome to app1.</h1></center></body></html>" > /var/www/html/index.html
RUN		chown root:apache /var/www/ -R

CMD		["/usr/sbin/apachectl", "-D", "FOREGROUND"]