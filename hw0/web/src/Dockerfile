FROM debian:bookworm-slim AS base

RUN apt-get -y update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libc6 \
    libstdc++6 \
    libprotobuf32 \
    libnl-route-3-200 \
    xz-utils && \
    rm -rf /var/lib/apt/lists/*

FROM kassany/bookworm-ziglang:0.15.1 AS app-builder

COPY app /app
WORKDIR /app
RUN zig build -Doptimize=ReleaseFast

FROM base AS nsjail-builder

RUN apt-get -y update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    autoconf \
    bison \
    flex \
    gcc \
    g++ \
    git \
    libprotobuf-dev \
    libnl-route-3-dev \
    libtool \
    make \
    pkg-config \
    protobuf-compiler && \
    rm -rf /var/lib/apt/lists/*

ADD https://github.com/google/nsjail.git /nsjail
WORKDIR /nsjail
RUN cd /nsjail && make clean && make -j$(nproc)

FROM debian:bookworm-slim AS chroot

RUN apt-get -y update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl && \
    rm -rf /var/lib/apt/lists/*

FROM base AS run

RUN groupadd -r ctf && useradd -r -g ctf -d /home/ctf -s /bin/bash ctf \
    && mkdir -p /home/ctf

COPY --from=chroot --chown=ctf:ctf / /chroot
COPY --from=nsjail-builder --chown=root:root --chmod=4755 /nsjail/nsjail /bin
COPY --from=app-builder --chown=ctf:ctf /app/zig-out/bin/server /server

USER ctf
WORKDIR /home/ctf

ENTRYPOINT [ "/server" ]
