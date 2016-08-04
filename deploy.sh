IMAGE_NAME="sportnumerics-predictor"

docker --version
virtualenv env
source env/bin/activate
pip install awscli
eval $(aws ecr get-login --region us-west-2)
docker build -t $IMAGE_NAME .
docker tag $IMAGE_NAME:latest 265978616089.dkr.ecr.us-west-2.amazonaws.com/$IMAGE_NAME:latest
docker push 265978616089.dkr.ecr.us-west-2.amazonaws.com/$IMAGE_NAME:latest
