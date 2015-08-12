#! /bin/sh

BROWSER_NAME="$1"
BROWSER_CHANNEL="$2"

ID=$(docker run -d \
  -e "BROWSER_NAME=$BROWSER_NAME" \
  -e "BROWSER_CHANNEL=$BROWSER_CHANNEL" \
  -p '0.0.0.0:4444:4444' \
  -e "VNC=1" \
  -p '0.0.0.0:5900:5900' \
  'wcpan/monitor:latest')

echo "$ID"
