FROM python:3.9

RUN mkdir -p /home/danmac5
WORKDIR /home/danmac5
COPY requirements.txt /home/danmac5
RUN pip install --upgrade pip --no-cache-dir -r requirements.txt

COPY . /home/danmac5
