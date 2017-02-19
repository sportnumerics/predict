FROM python:2
WORKDIR /code
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD predictor .
ADD go.py .
CMD python go.py
