set -e

# for native compilation, gcc is not available unless we initialise lambci gcc
. ~/init/gcc
pip install --user virtualenv
virtualenv env
source env/bin/activate
pip install -r requirements.txt
npm install serverless

./decrypt.sh
source ./config/env.sh
unset AWS_SESSION_TOKEN

SLS_DEBUG=* node_modules/.bin/serverless deploy --stage=dev --verbose
