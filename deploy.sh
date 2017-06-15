#!/bin/bash

set -e

if [ "$LAMBCI_BRANCH" = "master" ]; then
  pip install --user awscli
  STACK_PREFIX="sportnumerics-predict"
  STAGE="prodgreen"
  if aws cloudformation describe-stacks --stack-name "$STACK_PREFIX-$STAGE"; then
    STAGE="prodblue"
  fi
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

SLS_DEBUG=* node_modules/.bin/sls deploy --stage=$STAGE --verbose

docker tag $IMAGE_NAME:latest $ACCOUNT.dkr.ecr.ap-southeast-2.amazonaws.com/$IMAGE_NAME:latest
docker push $ACCOUNT.dkr.ecr.ap-southeast-2.amazonaws.com/$IMAGE_NAME:latest
