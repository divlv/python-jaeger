FROM python:3.9-alpine

RUN mkdir /cache

RUN sed -i -- 's/^app\.run/#&/' ./app/main.py

COPY ./app/ /app/
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install -r requirements.txt


CMD ["gunicorn", "-w 2", "-b 0.0.0.0:80", "main:app"]
