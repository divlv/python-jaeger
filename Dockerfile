FROM python:3.9-alpine

RUN mkdir /cache

COPY ./app/ /app/
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install -r requirements.txt

CMD sed -i -- 's/^app\.run/#&/' ./main.py

CMD ["gunicorn", "-w 4", "-b 0.0.0.0:80", "main:app"]
