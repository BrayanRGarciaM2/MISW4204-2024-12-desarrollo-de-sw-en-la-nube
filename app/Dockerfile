FROM python:3.10

ENV DB_HOST "db"

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD exec gunicorn --bind :5000 --workers 1 --threads 8 --timeout 0 app:app