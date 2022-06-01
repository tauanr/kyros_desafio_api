FROM python:3
ADD . /code
WORKDIR /code
ENV FLASK_APP api.py
RUN pip install -r requirements.txt
CMD flask run
