
FROM python:3.9.6-slim-buster


WORKDIR /app
COPY . /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 80
ENV NAME test

CMD ["python", "app.py"]