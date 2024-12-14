FROM node:20-slim AS build_web

COPY ./app /usr/src/app/app
COPY ./src /usr/src/app/server

WORKDIR /usr/src/app

RUN cd app && npm install && npm run build

RUN mkdir -p server/static \
    && cp -r app/build/* server/static \
    && cp -r server/static/static/* server/static \
    && rm -rf server/static/static \
    && rm -rf app

FROM debian:stable-slim

RUN apt-get update && apt-get install -y ffmpeg procps --no-install-recommends && rm -rf /var/lib/apt/lists/*

COPY --from=build_web /usr/src/app/server /usr/src/app/

COPY --link --from=ghcr.io/astral-sh/uv:0.5.2 /uv /usr/local/bin/uv

WORKDIR /usr/src/app

RUN chmod -R 777 /usr/src/app

RUN uv python install 3.10

COPY .python-version pyproject.toml .

RUN uv sync -v

RUN mkdir -p /data

EXPOSE 8000

#CMD ["sleep", "infinity"]

CMD ["uv", "run", "main.py"]