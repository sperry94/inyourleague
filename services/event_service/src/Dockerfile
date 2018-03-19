from node:carbon

WORKDIR user/src/eventsvc

COPY package*.json ./

RUN npm install --only=production

COPY . .

EXPOSE 8888

CMD ["npm", "start"]