```
docker build  --no-cache -t abc_msa_order .
docker run -itd  -p 8005:8080 --mount source=order_volume,target=/app_data --name order_container abc_msa_order
```


# Setting Mysql
https://stackoverflow.com/questions/39281594/error-1698-28000-access-denied-for-user-rootlocalhost
```
mysql -u root # I had to use "sudo" since it was a new installation

mysql> USE mysql;
mysql> SELECT User, Host, plugin FROM mysql.user;

+------------------+-----------------------+
| User             | plugin                |
+------------------+-----------------------+
| root             | auth_socket           |
| mysql.sys        | mysql_native_password |
| debian-sys-maint | mysql_native_password |
+------------------+-----------------------+

```
As you can see in the query, the ``root`` user is using the ``auth_socket`` plugin.

There are two ways to solve this:

You can set the root user to use the ``mysql_native_password`` plugin
You can create a new ``db_user`` with you ``system_user`` (recommended)
## Option 1:

```
sudo mysql -u root # I had to use "sudo" since it was a new installation

mysql> USE mysql;
mysql> UPDATE user SET plugin='mysql_native_password' WHERE User='root';
mysql> FLUSH PRIVILEGES;
mysql> exit;

sudo service mysql restart
```
## Creating Database
```
mysql> create database abc_msa;
Query OK, 1 row affected (0.01 sec)

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| abc_msa            |
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
5 rows in set (0.01 sec)
```
 
# 4 Ways You Can Connect Python to MySQL
If you are on a Linux machine, install the Python 3 and MySQL development headers and libraries first.
```
# Debian / Ubuntu
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
 
# Red Hat / CentOS
sudo yum install python3-devel mysql-devel
```
## Connect to MySQL Using mysqlclient
The [mysqlclient](https://www.mysql.com/products/connector/) driver is an interface to the MySQL database server that provides the Python database server API. It is written in C.
```
pip install mysqlclient
```

Connect to MySQL using the following connection code.
```python
import MySQLdb
 
connection = MySQLdb.connect(
    host="localhost",
    user="<mysql_user>",
    passwd="<mysql_password>",
    db="<database_name>"
)
 
cursor = connection.cursor()
cursor.execute("select database();")
db = cursor.fetchone()
 
if db:
    print("You're connected to database: ", db)
else:
    print('Not connected.')
```
## Connect to MySQL Using mysql-connector-python
The [mysql-connector-python](https://dev.mysql.com/doc/connector-python/en/) is the official connection driver supported by Oracle. It is also written in pure Python.
```bash
pip install mysql-connector-python
```

Connect to MySQL using the following connection code.
```python
import mysql.connector
from mysql.connector import Error
 
connection = mysql.connector.connect(host="localhost",
    user="<mysql_user>",
    passwd="<mysql_password>",
    db="<database_name>")
 
try:
    if connection.is_connected():
        cursor = connection.cursor()
        cursor.execute("select database();")
        db = cursor.fetchone()
        print("You're connected to dtabase: ", db)
except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
```
## Connect to MySQL Using PyMySQL
The [PyMySQL](https://pypi.org/project/pymysql/) connection driver is a replacement for MySQLdb. To use it, you need to be running Python 3.7 or newer and your MySQL server should be version 5. 7, or newer. If you use MariaDB it should be version 10.2 or higher. You can find these requirements on the [PyMySQL Github page](https://github.com/PyMySQL/PyMySQL).
```bash
pip install PyMySQL
```
Connect to MySQL using PyMySQL using this code.
```python
import pymysql
 
connection = pymysql.connect(host="localhost",
    user="<mysql_user>",
    password="<mysql_password>",
    database="<database_name>")
 
try:
    cursor = connection.cursor()
    cursor.execute("select database();")
    db = cursor.fetchone()
    print("You're connected to database: ", db)
except pymysql.Error as e:
    print("Error while connecting to MySQL", e)
finally:
    cursor.close()
    connection.close()
    print("MySQL connection is closed")
```

# Run multiple services in a container
* https://docs.docker.com/config/containers/multi-service_container/
* https://phoenixnap.com/kb/bash-wait-command

