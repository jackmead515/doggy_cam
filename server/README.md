FROM debian:stable-slim

COPY --link --from=ghcr.io/astral-sh/uv:0.5.2 /uv /usr/local/bin/uv

WORKDIR /app

RUN uv python install 3.10

COPY .python-version pyproject.toml .

RUN uv sync

COPY src ./src

COPY hapa.pt .

CMD ["uv", "run", "src/main.py"]