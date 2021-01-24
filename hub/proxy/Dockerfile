FROM node:alpine AS builder
WORKDIR /build

COPY package.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /build/build /usr/share/nginx/html
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
