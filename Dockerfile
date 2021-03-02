FROM python:3.8.8

ADD . .

RUN apt-get install tk && python3 -m pip install -r requirements.txt