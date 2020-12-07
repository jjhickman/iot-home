FROM node:alpine

RUN adduser -S notifier -G node; \
    mkdir -p /home/notifier

WORKDIR /home/notifier
COPY package.json .
RUN npm config set registry http://registry.npmjs.org/  \
    && npm install

COPY . .

RUN chown -R notifier /home/notifier
USER notifier
CMD ["npm", "start"]