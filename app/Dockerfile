FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

#CMD ["python", "./app.py"]
CMD exec gunicorn --bind :5000 --workers 1 --threads 8 --timeout 0 app:app
