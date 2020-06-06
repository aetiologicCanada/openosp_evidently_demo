FROM python:3.7.7-buster
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
COPY app.py /app/app.py
COPY config.yml app/config.yml
COPY scripts scripts
WORKDIR /app
CMD ["python", "app.py"]
