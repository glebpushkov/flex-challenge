FROM python:3.12.0-alpine

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY main.py /app/main.py
CMD ["python", "main.py", "-h"]
