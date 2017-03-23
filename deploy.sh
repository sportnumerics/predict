#!/bin/bash

set -e

if [ "$LAMBCI_BRANCH" = "master" ]; then
  STAGE=prod
else
  STAGE=dev
fi

IMAGE_NAME="sportnumerics-predictor-$STAGE"
ACCOUNT="265978616089"

./decrypt.sh
source ./config/env.sh
unset AWS_SESSION_TOKEN

docker --version
eval $(aws ecr get-login --region ap-southeast-2)
docker build -t $IMAGE_NAME .
docker tag $IMAGE_NAME:latest $ACCOUNT.dkr.ecr.ap-southeast-2.amazonaws.com/$IMAGE_NAME:latest

SLS_DEBUG=* node_modules/.bin/sls deploy --stage=$STAGE --verbose

docker push $ACCOUNT.dkr.ecr.ap-southeast-2.amazonaws.com/$IMAGE_NAME:latest
