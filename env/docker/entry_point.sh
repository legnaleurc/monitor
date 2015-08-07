#!/bin/bash

export GEOMETRY="$SCREEN_WIDTH""x""$SCREEN_HEIGHT""x""$SCREEN_DEPTH"

if [ -z "$BROWSER_NAME" ] || [ -z "$BROWSER_CHANNEL" ] ; then
  echo Invalid browser. 1>&2
  exit 1
fi

function shutdown {
  kill -s SIGTERM $NODE_PID
  wait $NODE_PID
}

function setup_google_chrome {
  channel="$1"

  setup_chromedriver

  google_chrome_url='https://dl.google.com/linux/direct'
  wget -q -O '/tmp/google_chrome.deb' "$google_chrome_url/google-chrome-stable_current_amd64.deb"
  # avoid to install hicolor-icon-theme
  sudo mkdir -p /usr/share/icons/hicolor
  sudo dpkg -i '/tmp/google_chrome.deb'
  rm -rf '/tmp/google_chrome.deb'

  sudo mv /opt/selenium/chrome_config.json /opt/selenium/config.json
}

function setup_chromedriver {
  chromedriver_version=$(wget -q -O - 'http://chromedriver.storage.googleapis.com/LATEST_RELEASE')
  chromedriver_url='http://chromedriver.storage.googleapis.com/%s/chromedriver_%s.zip'
  chromedriver_url=$(printf "$chromedriver_url" $chromedriver_version 'linux64')
  chromedriver_zip_path='/tmp/chromedriver_linux64.zip'
  chromedriver_path='/opt/selenium'

  wget -q -O "$chromedriver_zip_path" "$chromedriver_url"
  sudo rm -rf "$chromedriver_path/chromedriver"
  sudo unzip "$chromedriver_zip_path" -d "$chromedriver_path"
  sudo rm "$chromedriver_zip_path"
  sudo mv "$chromedriver_path/chromedriver" "$chromedriver_path/chromedriver-$chromedriver_version"
  sudo chmod 755 "$chromedriver_path/chromedriver-$chromedriver_version"
  sudo ln -fs "$chromedriver_path/chromedriver-$chromedriver_version" /usr/bin/chromedriver
}

setup_google_chrome $BROWSER_CHANNEL

# TODO: Look into http://www.seleniumhq.org/docs/05_selenium_rc.jsp#browser-side-logs

xvfb-run --server-args="$DISPLAY -screen 0 $GEOMETRY -ac +extension RANDR" \
  java -jar /opt/selenium/selenium-server-standalone.jar &
NODE_PID=$!

trap shutdown SIGTERM SIGINT
wait $NODE_PID
