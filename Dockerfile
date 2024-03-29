# syntax=docker/dockerfile:1

FROM python:3.10

WORKDIR /bromley-waste-scraper

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m", "flask", "--app=FlaskApp.py", "run", "--host=0.0.0.0" ]