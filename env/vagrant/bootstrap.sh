#! /bin/sh

# update repository
apt-get update

# setup Docker
apt-get install -y docker.io
# grant permission
adduser vagrant docker
# restart Docker
service docker.io stop
sleep 1
service docker.io start
# install Selenium Grid Hub
docker run -d -p 4444:4444 --name grid_hub selenium/hub
# install Chrome Node
docker run -d --link grid_hub:hub --name node_chrome selenium/node-chrome
# install Firefox Node
docker run -d --link grid_hub:hub --name node_firefox selenium/node-firefox
