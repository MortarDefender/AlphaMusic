# syntax=docker/dockerfile:1
FROM python:3.7

WORKDIR /app

COPY requirments.txt requirments.txt

RUN pip install -r requirments.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]