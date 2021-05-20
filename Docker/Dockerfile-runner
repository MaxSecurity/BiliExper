FROM python:3.8.3-alpine
MAINTAINER 星辰

RUN apk add --no-cache build-base libffi-dev \
 && pip --no-cache-dir install aiohttp requests json5 \
 && rm -rf ~/.cache/pip \
 && rm -rf /tmp/* \
 && apk del libffi-dev build-base

COPY entrypoint.sh ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]