FROM selenium/node-base:latest
MAINTAINER wcpan

USER root

COPY entry_point.sh /opt/bin/entry_point.sh
RUN chmod +x /opt/bin/entry_point.sh
COPY chrome_config.json /opt/selenium/chrome_config.json

USER seluser
#RUN apt-get update && apt-get install --no-install-recommends -y git
#WORKDIR /usr/local/src
#RUN git clone https://github.com/legnaleurc/monitor.git
#WORKDIR /usr/local/src/monitor
#RUN pip install -r requirements.txt
