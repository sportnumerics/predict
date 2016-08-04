FUNCTION_NAME="sportnumerics-predictor"
PACKAGE="build/package.zip"
ZIP_FILE_NAME="fileb://$PACKAGE"

if aws --region us-west-2 lambda get-function --function-name $FUNCTION_NAME ; then
  echo "Updating $FUNCTION_NAME..."
  aws --region us-west-2 lambda update-function-code --function-name $FUNCTION_NAME --zip-file $ZIP_FILE_NAME --publish
else
  echo "Creating $FUNCTION_NAME..."
  aws --region us-west-2 lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime python2.7 \
    --role "arn:aws:iam::265978616089:role/lambda_basic_execution" \
    --handler go.handler \
    --zip-file $ZIP_FILE_NAME \
    --description "Sportnumerics predictor" \
    --publish true
fi
