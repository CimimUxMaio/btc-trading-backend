FROM python:3.8.8

WORKDIR /app_src

ADD requirements.txt .

RUN apt-get install tk && python3 -m pip install -r requirements.txt

CMD python main.py

COPY . .