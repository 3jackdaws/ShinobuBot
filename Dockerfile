FROM python:latest
RUN apt-get update
RUN apt-get install -y git python3-pip libopus0 libav-tools
RUN pip3 install discord.py cleverbot PyNaCl youtube_dl pafy

WORKDIR /etc
RUN git clone http://github.com/3jackdaws/ShinobuBot
EXPOSE 55000
WORKDIR /etc/ShinobuBot
ENTRYPOINT ["bash"]
