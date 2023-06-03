FROM python:3.11-alpine

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1
CMD python main.py