FROM node:slim

WORKDIR /notifier
COPY . /notifier

RUN npm install

RUN curl -sf https://gobinaries.com/tj/node-prune | sh; \
    node-prune

CMD ["npm", "start"]