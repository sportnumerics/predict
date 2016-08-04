docker --version
virtualenv env
source env/bin/activate
pip install awscli
eval $(aws ecr get-login --region us-west-2)
docker build -t sportnumerics-predictor .
docker tag sportnumerics-predictor:latest 265978616089.dkr.ecr.us-west-2.amazonaws.com/sportnumerics-predictor:latest
docker push 265978616089.dkr.ecr.us-west-2.amazonaws.com/sportnumerics-predictor:latest
