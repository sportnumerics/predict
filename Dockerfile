FROM python:3
WORKDIR /code
ADD requirements.txt .
RUN pip --no-cache-dir install -r requirements.txt
ADD predictor predictor
ADD go.py .
CMD python go.py
