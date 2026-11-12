# Copyright (C) @itsSmartDev

FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DENO_INSTALL=/usr/local \
    SESSION_DIR=/app/data

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg tini ca-certificates curl unzip \
 && curl -fsSL https://deno.land/install.sh | sh -s -- -y --no-modify-path \
 && apt-get purge -y curl unzip && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt \
 && pip install -U "yt-dlp[default]"

COPY . .

RUN mkdir -p downloads cache logs data cookies

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "bot.py"]
