FROM python:2.7-slim

WORKDIR /iyl

COPY requirements.txt .

RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . .

RUN pip install ./inyourleague

EXPOSE 8000

CMD gunicorn -b 0.0.0.0:$PORT inyourleague:app