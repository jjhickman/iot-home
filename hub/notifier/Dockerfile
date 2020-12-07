FROM node:stretch-slim

WORKDIR /notifier
COPY . /notifier

RUN npm config set registry http://registry.npmjs.org/  \
    && npm install

EXPOSE 5672
EXPOSE 8080
EXPOSE 80
EXPOSE 443

CMD ["npm", "start"]