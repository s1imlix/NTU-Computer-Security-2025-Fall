FROM php:8.4-apache

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    iputils-ping && \
    apt-get purge curl -y && \
    rm -rf /var/lib/apt/lists/*

COPY --chown=root:root --chmod=444 flag.txt /flag.txt
RUN target_dir="/flag_$(tr -dc A-Za-z0-9 </dev/urandom | head -c32)" && \
    flag_name="flag_$(tr -dc A-Za-z0-9 </dev/urandom | head -c32).txt" && \
    mkdir -p "$target_dir" && \
    mv /flag.txt "$target_dir/$flag_name"
COPY --chown=www-data:www-data --chmod=500 src /var/www/html/

# Automatically restarts in case something goes wrong
ENTRYPOINT [ "timeout", "10m", "apache2-foreground"]
