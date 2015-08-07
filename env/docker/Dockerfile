FROM selenium/node-base:latest
MAINTAINER wcpan

USER root

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
  xdg-utils

COPY entry_point.sh /opt/bin/entry_point.sh
RUN chmod +x /opt/bin/entry_point.sh
COPY chrome_config.json /opt/selenium/chrome_config.json

USER seluser
#RUN apt-get update && apt-get install --no-install-recommends -y git
#WORKDIR /usr/local/src
#RUN git clone https://github.com/legnaleurc/monitor.git
#WORKDIR /usr/local/src/monitor
#RUN pip install -r requirements.txt
