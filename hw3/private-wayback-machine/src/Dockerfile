FROM alpine AS builder

RUN apk add --no-cache build-base
COPY flag/readflag.c /src/
WORKDIR /src
RUN gcc -static readflag.c -o readflag

FROM php:8.4-apache

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y unzip libmemcached-dev zlib1g-dev && \
    pecl install mongodb && \
    docker-php-ext-enable mongodb && \
    pecl install memcached && \
    docker-php-ext-enable memcached && \
    rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite && \
    a2enmod actions

# Setup flag & readflag
COPY --from=builder --chown=root:root --chmod=4555 /src/readflag /
COPY --chown=root:root --chmod=400 flag/flag /

# Setup webapp
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer
COPY webapp /var/www/html/
WORKDIR /var/www/html/
RUN composer install
