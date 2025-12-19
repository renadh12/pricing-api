FROM python:3.11-slim

WORKDIR /app

RUN pip install kafka-python redis python-snappy

COPY consumer.py .

CMD ["python", "consumer.py"]