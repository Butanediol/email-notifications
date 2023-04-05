FROM python:3.11

WORKDIR /app
COPY . .
RUN pip install requests

ENV PYTHONUNBUFFERED=1
CMD python main.py