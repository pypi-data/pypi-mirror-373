# syntax=docker/dockerfile:1
FROM php:{{ php_version }}-alpine

RUN apk update

{% for package in apk_packages %}
RUN apk add {{ package }} || true
{% endfor %}

{% for extension in php_extensions %}
RUN docker-php-ext-install {{ extension }} || true
{% endfor %}

{% for extension in pecl_extensions %}
RUN pecl install {{ extension }} || true
RUN docker-php-ext-enable {{ extension }} || true
{% endfor %}

RUN npm install --global yarn

COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer
RUN echo 'memory_limit = 8G' > /usr/local/etc/php/conf.d/docker-php-memlimit.ini
RUN echo 'xdebug.mode=coverage' > /usr/local/etc/php/conf.d/docker-php-xdebug.ini
RUN echo 'xdebug.start_with_request=yes' >> /usr/local/etc/php/conf.d/docker-php-xdebug.ini
RUN echo 'xdebug.client_host=host.docker.internal' >> /usr/local/etc/php/conf.d/docker-php-xdebug.ini
RUN echo 'xdebug.client_port=9003' >> /usr/local/etc/php/conf.d/docker-php-xdebug.ini

RUN echo 'auto_prepend_file = /coverage-collector.php' > /usr/local/etc/php/conf.d/docker-php-coverage.ini

# disable mysql client ssl
RUN mkdir -p /etc/mysql && echo "[mysql]\nskip-ssl" > /etc/mysql/my.cnf

# Copy the coverage collector script
COPY ./coverage-collector.php /coverage-collector.php

# Install swagger-php globally
RUN --mount=type=cache,target=/tmp/composer/cache \
    COMPOSER_CACHE_DIR=/tmp/composer/cache COMPOSER_HOME=/root/.composer-legacy composer global require zircote/swagger-php:4.7.16

RUN --mount=type=cache,target=/tmp/composer/cache \
    COMPOSER_CACHE_DIR=/tmp/composer/cache COMPOSER_HOME=/root/.composer-modern composer global require zircote/swagger-php:5.3.1

# Create app directory
WORKDIR /app

# Copy the rest of the application code
COPY ./src ./

RUN if [ -f .env.example ]; then cp .env.example .env; fi

# Install composer dependencies with cache mount for faster builds
RUN --mount=type=cache,target=/tmp/composer/cache \
    COMPOSER_CACHE_DIR=/tmp/composer/cache composer install --no-dev --optimize-autoloader || true

# Install composer requirements
{% for requirement in composer_requirements %}
RUN --mount=type=cache,target=/tmp/composer/cache \
    COMPOSER_CACHE_DIR=/tmp/composer/cache composer require {{ requirement }} || true
{% endfor %}

# Disable throttle middleware
RUN find . -path "*/Http/Kernel.php" -exec sed -i "/^\s*'throttle:\d+,\d+'/d" {} \;

# Install yarn dependencies if yarn.lock exists
RUN if [ -f yarn.lock ]; then yarn install || true; fi
RUN if [ -f yarn.lock ]; then yarn build || true; fi

# Install npm dependencies if package-lock.json exists
RUN if [ -f package-lock.json ]; then npm install || true; fi
RUN if [ -f package-lock.json ]; then npm run build || true; fi

COPY --from=ghcr.io/wangyihang/php-function-extractor:latest /app/bin/php-function-extractor.phar /usr/local/bin/php-function-extractor
RUN chmod +x /usr/local/bin/php-function-extractor

WORKDIR /app/public
ENTRYPOINT [ "php", "-S", "0.0.0.0:80" ]
