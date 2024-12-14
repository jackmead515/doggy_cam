FROM node:20-slim

WORKDIR /usr/src/app

COPY ./package.json /usr/src/app

RUN npm install

COPY ./src /usr/src/app

EXPOSE 5454

CMD ["node", "index.js"]