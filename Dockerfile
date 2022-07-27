FROM python:3.9

RUN mkdir -p /home/project/danmac5
WORKDIR /home/project/danmac5
COPY requirements.txt /home/project/danmac5
RUN pip install --upgrade pip --no-cache-dir -r requirements.txt

COPY . /home/project/danmac5
