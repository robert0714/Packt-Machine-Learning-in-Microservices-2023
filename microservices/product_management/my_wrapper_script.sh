#!/bin/bash

# Start the first process


/usr/sbin/service mysql start   

/usr/bin/mysql  -u root -D  mysql -e " UPDATE user SET plugin='mysql_native_password' WHERE User='root'  " 
 
/usr/bin/mysql  -u root -D  mysql -e "  create database abc_msa  "  

/usr/bin/mysql  -u root -D  mysql -e "  FLUSH PRIVILEGES  "   

echo 'Begin..........RESTART MYSQL'   

/usr/sbin/service mysql restart  

while ! mysqladmin ping -h "localhost"  --silent; do
    echo "Waiting for database connection..."
    sleep 1
done 

echo 'Finish..........RESTART MYSQL'  &


# Wait for any process to start flask
wait -n
  
echo 'Begin..........Wait 1 Min'  

# flask run -h 0.0.0.0 -p 8080  --debug
flask run -h 0.0.0.0 -p 8080  
