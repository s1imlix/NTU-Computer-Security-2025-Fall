FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -qy socat

RUN useradd -m chal
WORKDIR /home/chal

RUN chown -R root:root . && chmod -R 755 .

USER chal
CMD socat TCP-LISTEN:1337,reuseaddr,fork EXEC:"./run.sh"
