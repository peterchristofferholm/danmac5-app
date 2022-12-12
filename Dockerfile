FROM python:3.9
WORKDIR /usr/src/danmac5
COPY requirements.txt ./
RUN pip install --upgrade pip --no-cache-dir -r requirements.txt
