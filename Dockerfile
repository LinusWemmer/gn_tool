FROM ubuntu:16.04

RUN apt-get update && apt-get -y install git swi-prolog sfst unzip wget python

RUN git clone https://github.com/rsennrich/ParZu

RUN (cd ParZu; bash install.sh)

WORKDIR /ParZu
CMD python parzu
