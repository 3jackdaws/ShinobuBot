FROM python:latest
RUN apt-get update
RUN apt-get install -y git python3-pip libopus0 libav-tools
RUN pip3 install discord.py cleverbot PyNaCl youtube_dl pafy

WORKDIR /etc
RUN mkdir shinobu

EXPOSE 55000
WORKDIR /etc
ADD start_shinobu.sh .
VOLUME /etc/shinobu
ENTRYPOINT ["sh", "/etc/start_shinobu.sh"]
