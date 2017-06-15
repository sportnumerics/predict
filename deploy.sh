#!/bin/bash

set -e

REGION="ap-southeast-2"

if [ "$LAMBCI_BRANCH" = "master" ]; then
  CDN_STACK_NAME="sportnumerics-explorer-cdn-prod"
  aws configure set region $REGION
  ACTIVE_DEPLOYMENT=$(aws cloudformation describe-stacks --stack-name $CDN_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ExplorerStageDeployment`].OutputValue' --output text)
  if [ "$ACTIVE_DEPLOYMENT" = "prodgreen" ]; then
    STAGE="prodblue"
    EXPLORER_API_PREFIX="explorer-api-blue"
  else
    STAGE="prodgreen"
    EXPLORER_API_PREFIX="explorer-api-green"
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
eval $(aws ecr get-login --region $REGION)
docker build -t $IMAGE_NAME .

SLS_DEBUG=* node_modules/.bin/sls deploy --stage=$STAGE --verbose

docker tag $IMAGE_NAME:latest $ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$IMAGE_NAME:latest
docker push $ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$IMAGE_NAME:latest
