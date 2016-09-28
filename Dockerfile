FROM python:latest
RUN apt-get update
RUN apt-get install -y git python3-pip libopus0 libav-tools
RUN pip3 install discord.py cleverbot PyNaCl youtube_dl pafy

WORKDIR /etc
RUN mkdir shinobu
RUN git clone http://github.com/3jackdaws/ShinobuBot

RUN cp -R /etc/ShinobuBot/* /etc/shinobu/
RUN rm -rf /etc/ShinobuBot
VOLUME /etc/shinobu/resources
EXPOSE 55000
WORKDIR /etc/shinobu
ENTRYPOINT ["python", "Shinobu.py"]