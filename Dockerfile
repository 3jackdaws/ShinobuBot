FROM python:latest
RUN apt-get update
RUN apt-get install -y git python3-pip libopus0 libav-tools
RUN pip3 install discord.py cleverbot PyNaCl youtube_dl pafy

WORKDIR /etc
RUN mkdir shinobu
RUN git clone http://github.com/3jackdaws/ShinobuBot

RUN cp -R /etc/ShinobuBot/* /etc/shinobu/
RUN rm -rf /etc/ShinobuBot
VOLUME /etc/shinobu
EXPOSE 55000
RUN mv /etc/shinobu/start_shinobu.sh /etc/
WORKDIR /etc
ENTRYPOINT ["bash", "start_shinobu.sh"]
