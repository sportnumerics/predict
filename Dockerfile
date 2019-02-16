FROM python:3
WORKDIR /code
RUN pipenv install
ADD predictor predictor
ADD go.py .
CMD python go.py
