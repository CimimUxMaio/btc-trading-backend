FROM python:3.8.8

WORKDIR /app_src

ADD requirements.txt heroku_run.sh ./

RUN apt-get install tk && python3 -m pip install -r requirements.txt && chmod +x heroku_run.sh

ENTRYPOINT python main.py False

COPY . .