# build step
FROM node:16.15.1-alpine as build
WORKDIR /templateweb
COPY package.json ./
RUN yarn install
COPY . /templateweb
#RUN yarn build

CMD ["yarn", "start", "--host", "0.0.0.0"]