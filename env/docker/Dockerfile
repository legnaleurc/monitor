FROM selenium/node-base:latest
MAINTAINER wcpan

USER root


# For Google Chrome:
#   gconf-service
#   libasound2
#   libatk1.0-0
#   libcairo2
#   libgconf-2-4
#   libgdk-pixbuf2.0-0
#   libgtk2.0-0
#   libpango1.0-0
#   libxcomposite1
#   libxss1
#   libxtst6
#   libappindicator1
#   libcurl3
#   xdg-utils
# For Mozilla Firefox:
#   python-pip
# For VNC:
#   x11vnc
RUN apt-get update && apt-get install -y --no-install-recommends \
  gconf-service \
  libasound2 \
  libatk1.0-0 \
  libcairo2 \
  libgconf-2-4 \
  libgdk-pixbuf2.0-0 \
  libgtk2.0-0 \
  libpango1.0-0 \
  libxcomposite1 \
  libxss1 \
  libxtst6 \
  libappindicator1 \
  libcurl3 \
  xdg-utils \
  python-pip \
  x11vnc \
  && rm -rf /var/lib/apt/lists/* \
  && pip install -U mozdownload mozInstall

COPY entry_point.sh /opt/bin/entry_point.sh
RUN chmod +x /opt/bin/entry_point.sh
COPY chrome_config.json /opt/selenium/chrome_config.json
COPY firefox_config.json /opt/selenium/firefox_config.json
COPY chrome_launcher.sh /opt/google/chrome/chrome_launcher.sh

USER seluser

RUN mkdir -p ~/.vnc \
  && x11vnc -storepasswd secret ~/.vnc/passwd
