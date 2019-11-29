FROM ubuntu:bionic

# Optimise environment variables
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 NOKOGIRI_USE_SYSTEM_LIBRARIES=true

# Install system packages (ruby, python, node and build libraries)
# Node ppa provided by: https://github.com/nodesource/distributions
RUN apt-get update && \
    apt-get install curl --yes && \
    curl -sL https://deb.nodesource.com/setup_12.x | bash - && \
    apt-get update && \
    apt-get install --yes \
        build-essential ruby-dev ruby-bundler python3-dev python3-pip \
        libpq-dev libjpeg-dev zlib1g-dev libpng-dev libmagickwand-dev \
        libjpeg-progs optipng git vim curl jq python-launchpadlib libsodium-dev \
        nodejs

# Supportive python tools for debugging, syntax checking and DB connectivity
RUN pip3 install --upgrade ipdb flake8 black python-swiftclient psycopg2 pymongo pipenv

# Latest Yarn package manager and bower
RUN npm install --global yarn bower

# Create a shared home directory - this helps anonymous users have a home
WORKDIR /home/shared
ENV HOME=/home/shared LANG=C.UTF-8 LC_ALL=C.UTF-8
RUN mkdir -p $HOME
RUN mkdir -p $HOME/.cache/yarn/
RUN mkdir -p $HOME/.cache/bower/
RUN chmod -R 777 $HOME

# SSH agent finds up home using /etc/passwd
# Fix for .ssh folder
RUN mkdir -p $HOME/.ssh
RUN ln -s $HOME/.ssh /root/.ssh
