FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1 

WORKDIR /usr/src/ngsdb

COPY ./requirements.txt /usr/src/ngsd/requirements.txt 
RUN pip install -r /usr/src/ngsd/requirements.txt

COPY . /usr/src/ngsdb/


EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]