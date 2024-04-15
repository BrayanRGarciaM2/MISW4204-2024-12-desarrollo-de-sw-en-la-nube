FROM python:3.10

WORKDIR /usr/src/celery

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y ffmpeg
COPY . .

RUN chmod +x /usr/src/celery/adjust_video.sh
RUN chmod +x /usr/src/celery/trim_video.sh
COPY . .