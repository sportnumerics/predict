FROM python:3
WORKDIR /code
RUN pip install --upgrade pipenv
RUN pipenv install
ADD predictor predictor
ADD go.py .
CMD python go.py
