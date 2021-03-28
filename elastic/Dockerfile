############################################################
# Dockerfile to build the Fit Games project
# Based on frolvlad/alpine-python3
############################################################
FROM ubuntu:18.04

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Installing, updating python3, pip and dependencies used by weasyprint and other libraries
RUN apt-get update
RUN apt-get install -y build-essential python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 \
libpangocairo-1.0.0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info gdal-bin libjpeg-dev zlib1g-dev
RUN apt-get install --fix-missing
RUN pip3 install --no-cache-dir --upgrade testresources pip setuptools

# Setup default encoding to UTF-8 - Needed to handle german characters
ENV LANG C.UTF-8

# Setup build args - These arguments are used to setup the docker image in build-time
ARG DB_NAME_ARG='elastic'
ARG DB_USER_ARG='postgres'
ARG DB_PASSWORD_ARG='postgres'
ARG DB_HOST_ARG='elastic-db'
ARG DB_PORT_ARG=5432

# Configure build env variables - Arguments are automatically used as DEFAULT ENV VARIABLES when executing 'docker run'
# When running 'docker run', any of the environment variables can be re-setted
ENV DB_NAME=$DB_NAME_ARG
ENV DB_USER=$DB_USER_ARG
ENV DB_PASSWORD=$DB_PASSWORD_ARG
ENV DB_HOST=$DB_HOST_ARG
ENV DB_PORT=$DB_PORT_ARG

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt
COPY . /usr/src/app

WORKDIR /usr/src/app

RUN /usr/bin/python3 ./manage.py collectstatic --no-input
# By default exporting 8080, since it's the port which GAE expects to use for comunicatting with the docker container
EXPOSE 8080

ENTRYPOINT ["./start.sh"]
