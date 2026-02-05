FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    icecast2 \
    python3 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY icecast.xml /etc/icecast2/icecast.xml
COPY start.sh /start.sh
RUN chmod +x /start.sh

RUN mkdir -p /music

EXPOSE 80

CMD ["/start.sh"]
