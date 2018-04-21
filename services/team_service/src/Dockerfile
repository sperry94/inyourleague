from node:carbon

WORKDIR user/src/teamsvc

COPY package*.json ./

RUN npm install --only=production

COPY . .

EXPOSE 8890

CMD ["npm", "start"]