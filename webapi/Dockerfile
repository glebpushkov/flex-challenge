FROM python:3.12.0-alpine

WORKDIR /webapi
COPY ./requirements.txt /webapi/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /webapi/requirements.txt
COPY ./app /webapi/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000
