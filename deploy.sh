#!/bin/bash

set -ex

AWS_DEFAULT_REGION=$(aws configure get region)
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

if [ "$LAMBCI_BRANCH" = "master" ]; then
  CDN_STACK_NAME="sportnumerics-explorer-cdn-prod"
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


SLS_DEBUG=* sls deploy --stage=$STAGE --verbose

IMAGE_NAME="sportnumerics-predictor-$STAGE"

docker --version
eval $(aws ecr get-login --region $AWS_DEFAULT_REGION)
docker build -t $IMAGE_NAME .

docker tag $IMAGE_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_NAME:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_NAME:latest
