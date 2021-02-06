FROM python:3.7
WORKDIR /code
RUN pip install --upgrade pipenv
ADD Pipfile .
ADD Pipfile.lock .
RUN pipenv install --system --deploy --ignore-pipfile
ADD predictor predictor
ADD go.py .
CMD python go.py
