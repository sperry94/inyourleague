from node:carbon

WORKDIR user/src/accountsvc

COPY package*.json ./

RUN npm install --only=production

COPY . .

EXPOSE 8889

CMD ["npm", "start"]