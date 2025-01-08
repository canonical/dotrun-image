FROM ubuntu:jammy

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV DISABLE_PIP_VERSION_CHECK=1
ENV NO_UPDATE_NOTIFIER=true

# Install essential system packages
RUN apt-get update && \
    apt-get install --yes \
    git curl wget build-essential python3-dev python3-pip

# Set up Node.js 21 repository
RUN curl -fsSL https://deb.nodesource.com/setup_21.x | bash -

# Install Node.js and dependencies
RUN apt-get install --yes nodejs haproxy libwayland-client0

# Install a compatible npm version
RUN npm install --location=global npm@10

# Install common dependencies used in projects
RUN apt-get install --yes \
    gettext libjpeg-dev libjpeg-progs libmagic1 gpg \
    libmagickwand-dev libpng-dev libpq-dev libsodium-dev \
    optipng zlib1g-dev libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libatspi2.0-0 libcairo2 libcups2 libdrm2 \
    libgbm1 libnss3 libpango-1.0-0 libx11-6 libxau6 libxcb1 \
    libxcomposite1 libxdamage1 libxdmcp6 libxext6 libxfixes3 \
    libxkbcommon-x11-0 libxrandr2 nodejs haproxy libwayland-client0

# Update npm and install yarn
RUN npm install --location=global npm
RUN npm install --location=global yarn

# Copy and install dotrun-docker
WORKDIR /tmp
ADD src src
RUN pip3 install ./src
RUN rm -r /tmp/*

# Create ubuntu user
RUN groupadd --gid 1000 ubuntu
RUN useradd -rm -d /home/ubuntu -s /bin/bash -g ubuntu -G sudo -u 1000 ubuntu
USER ubuntu
WORKDIR /home/ubuntu
