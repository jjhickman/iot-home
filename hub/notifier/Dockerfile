FROM node:alpine

WORKDIR /notifier
COPY package.json .
RUN npm config set registry http://registry.npmjs.org/  \
    && npm install --production

COPY . .

CMD ["npm", "start"]