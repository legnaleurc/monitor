#! /bin/sh

echo '
deb http://httpredir.debian.org/debian jessie-updates main
deb-src http://httpredir.debian.org/debian jessie-updates main

deb http://httpredir.debian.org/debian jessie-backports main
deb-src http://httpredir.debian.org/debian jessie-backports main' >> '/etc/apt/sources.list'
# update repository
apt-get update

# setup Docker
apt-get install -y --no-install-recommends docker.io
# grant permission
adduser vagrant docker
