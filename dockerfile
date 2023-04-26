FROM python:3.9-buster

WORKDIR /app
COPY . /app

RUN echo "deb http://ftp.kz.debian.org/debian/ buster main" > /etc/apt/sources.list && \
    echo "deb http://ftp2.kz.debian.org/debian/ buster main" >> /etc/apt/sources.list && \
    echo "deb http://mirror.alcom.kz/debian/ buster main" >> /etc/apt/sources.list && \
    echo "deb http://mirror.ps.kz/debian/ buster main" >> /etc/apt/sources.list && \
    echo "deb http://mirror.numericable.fr/debian/ buster main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

EXPOSE 80
ENV NAME test

CMD ["python", "app.py"]