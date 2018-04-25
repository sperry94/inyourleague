#! /bin/bash

# log in to heroku
heroku login
heroku container:login

echo "$1"

# deploy database
if [ "$#" -eq 0 ] || [ "$1" = "db" ] ; then
  cd database/src
  heroku pg:psql -a iyl-svc-event < Create_IYL.sql
  cd ../..
fi

# deploy account service
if [ "$#" -eq 0 ] || [ "$1" = "account" ] ; then
  cd services/account_service/src
  heroku container:push web --app iyl-svc-account
  cd ../../..
fi

# deploy event service
if [ "$#" -eq 0 ] || [ "$1" = "event" ] ; then
  cd services/event_service/src
  heroku container:push web --app iyl-svc-event
  cd ../../..
fi

# deploy team service
if [ "$#" -eq 0 ] || [ "$1" = "team" ] ; then
  cd services/team_service/src
  heroku container:push web --app iyl-svc-team
  cd ../../..
fi

# deploy web-app
if [ "$#" -eq 0 ] || [ "$1" = "webapp" ] ; then
  cd web-app/src
  heroku container:push web --app iyl-webapp
  cd ../..
fi
