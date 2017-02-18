#!/bin/bash

STAGE="dev"
IMAGE_NAME="sportnumerics-predictor-$STAGE"
ACCOUNT="265978616089"

docker --version
eval $(aws ecr get-login --region ap-southeast-2)
docker build -t $IMAGE_NAME .
docker tag $IMAGE_NAME:latest $ACCOUNT.dkr.ecr.ap-southeast-2.amazonaws.com/$IMAGE_NAME:latest
docker push $ACCOUNT.dkr.ecr.ap-southeast-2.amazonaws.com/$IMAGE_NAME:latest
