# Docker File for "customer_management" microservice
FROM ubuntu:22.10

LABEL maintainer="Jian-De Lee <robert0714@gmail.com>"
LABEL description="This example Dockerfile for 'customer_management' microservice."
MAINTAINER Jian-De Lee <robert0714@gmail.com>

RUN sed -i 's/archive.ubuntu.com/tw.archive.ubuntu.com/g' /etc/apt/sources.list  

# Install some dependencies/packages
RUN apt-get update && \
    apt-get install -y apt-transport-https net-tools mysql-server python3 pip git build-essential curl wget vim software-properties-common;

# Install OpenJDK
RUN  apt-get install -y default-jdk

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/

# Install Flask to run our application and respond to API calls
RUN pip install -U flask && \
    pip install -U mysql-connector-python
    
# Expose port TCP/8080 to listen the container's application/flask API calls
EXPOSE 8080

# Create the /app_data directory and make it the working directory in the container
RUN mkdir /app_data
WORKDIR /app_data
ENV PATH $PATH:/app_data
 
COPY  ./my_wrapper_script.sh  /app_data/my_wrapper_script.sh
COPY  ./customer_management_ms.py  /app_data/microservices/customer_management/customer_management_ms.py 

# Initialize the flask app
ENV FLASK_APP /app_data/microservices/customer_management/customer_management_ms.py 
ENV MYSQL_DATABASE=abc_msa
ENV TZ=Asia/Taipei

# Specify a mount point in the container
VOLUME /app_data

# Start mysql & flask services and available bash sheel 
RUN chmod +x /app_data/my_wrapper_script.sh 
RUN ["/usr/sbin/usermod", "-d", "/var/lib/mysql/", "mysql"]    
  
CMD ["/bin/bash", "-c", "echo FIRST COMMAND;echo SECOND COMMAND;/app_data/my_wrapper_script.sh "]