FROM ubuntu

RUN apt update 
RUN apt-get install python3.8 -y
RUN apt install python3-pip -y

RUN mkdir /bot
WORKDIR /bot
COPY req.txt /req.txt
RUN pip3 install -r /req.txt && rm /req.txt

