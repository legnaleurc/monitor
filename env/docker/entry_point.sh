#!/bin/bash

export GEOMETRY="$SCREEN_WIDTH""x""$SCREEN_HEIGHT""x""$SCREEN_DEPTH"

if [ -z "$BROWSER_NAME" ] || [ -z "$BROWSER_CHANNEL" ] ; then
  echo 'Invalid browser.' 1>&2
  exit 1
fi

function shutdown {
  kill -s SIGTERM $NODE_PID
  wait $NODE_PID
}

function setup_google_chrome {
  channel="$1"
  if [ "$channel" = 'dev' ] ; then
    channel='unstable'
  elif [ "$channel" != 'stable' ] && [ "$channel" != 'beta' ] ; then
    echo 'Invalid channel.' 1>&2
    exit 1
  fi

  setup_chromedriver

  google_chrome_url='https://dl.google.com/linux/direct'
  google_chrome_path='/tmp/google_chrome.deb'
  wget -q -O "$google_chrome_path" "$google_chrome_url/google-chrome-${channel}_current_amd64.deb"
  # avoid to install hicolor-icon-theme
  sudo mkdir -p /usr/share/icons/hicolor
  sudo dpkg -i "$google_chrome_path"
  rm -rf "$google_chrome_path"

  sudo mv /opt/selenium/chrome_config.json /opt/selenium/config.json
}

function setup_chromedriver {
  chromedriver_version=$(wget -q -O - 'http://chromedriver.storage.googleapis.com/LATEST_RELEASE')
  chromedriver_url="http://chromedriver.storage.googleapis.com/$chromedriver_version/chromedriver_linux64.zip"
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

function setup_mozilla_firefox {
  channel="$1"
  firefox_tarball_path='/tmp/firefox.tar.bz2'
  type='release'
  version='latest'
  branch='mozilla-central'

  case "$channel" in
    esr)
      version='latest-esr'
    ;;
    release)
    ;;
    beta)
      version='latest-beta'
    ;;
    aurora)
      type='daily'
      branch='mozilla-aurora'
    ;;
    nightly)
      type='daily'
    ;;
    *)
      echo "Unknown channel." 1>&2
      exit 1
    ;;
  esac

  mozdownload -a 'firefox' -d "$firefox_tarball_path" -l 'en-US' -p 'linux64' -t "$type" -v "$version" --branch="$branch"
  sudo mozinstall -d '/opt' "$firefox_tarball_path"
  rm "$firefox_tarball_path"

  sudo mv /opt/selenium/firefox_config.json /opt/selenium/config.json
}

if [ "$BROWSER_NAME" = 'chrome' ] ; then
  setup_google_chrome "$BROWSER_CHANNEL"
elif [ "$BROWSER_NAME" = 'firefox' ] ; then
  setup_mozilla_firefox "$BROWSER_CHANNEL"
else
  echo "Unknown browser." 1>&2
  exit 1
fi

# TODO: Look into http://www.seleniumhq.org/docs/05_selenium_rc.jsp#browser-side-logs

xvfb-run --server-args="$DISPLAY -screen 0 $GEOMETRY -ac +extension RANDR" \
  java -jar /opt/selenium/selenium-server-standalone.jar &
NODE_PID=$!

trap shutdown SIGTERM SIGINT
wait $NODE_PID
