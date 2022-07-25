FROM python:3.9.7

RUN apt-get update && apt-get install -y python3-pip

RUN python3 -m pip install --upgrade pip

COPY requirements.txt /requirements.txt

RUN python3 -m pip install -r requirements.txt

RUN rm /requirements.txt

COPY script.py /script.py

WORKDIR /

ENTRYPOINT ["python", "script.py"]




