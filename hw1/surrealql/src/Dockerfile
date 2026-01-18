FROM node:22-alpine

COPY --chown=node:node src /home/node/app
WORKDIR /home/node/app
USER node
RUN npm install

ENTRYPOINT [ "node", "index.js" ]
