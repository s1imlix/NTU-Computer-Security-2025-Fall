FROM node:22-alpine

RUN apk add --no-cache chromium

RUN adduser -D -s /bin/sh bot
USER bot
WORKDIR /app
COPY --chown=bot:bot package.json .
ARG PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
RUN npm install
COPY --chown=bot:bot . .

CMD ["npm", "start"]
