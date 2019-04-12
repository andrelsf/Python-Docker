FROM	centos:latest

LABEL	app2.version="1.0" \
		app2.vendor="Andre L S Ferreira" \
		app2.description="MeetUP DevOPs App 2."

RUN		yum makecache fast \
		&& yum install epel-release -y \
		&& yum install httpd httpd-tools -y

RUN		echo "<html><body><br><center><h1>Welcome to APP2.</h1></center></body></html>" > /var/www/html/index.html
RUN		chown root:apache /var/www/ -R

CMD		["/usr/sbin/apachectl", "-D", "FOREGROUND"]
