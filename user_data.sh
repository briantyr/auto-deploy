#!/bin/sh
set -e -x

apt-get --yes --quiet update
apt-get --yes --quiet install nginx
rm /etc/nginx/sites-enabled/default
cat << 'EOF' > /etc/nginx/sites-available/automation


server {
    listen 80 default_server;
    root /usr/share/nginx/html;
    index automation.html;
    server_name localhost;
    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

    
cat << 'EOF' > /usr/share/nginx/html/automation.html
<html><head></head><body><h1><center>Automation for the people!</center></h1></body></html>

EOF

ln -s /etc/nginx/sites-available/automation /etc/nginx/sites-enabled
/etc/init.d/nginx restart
