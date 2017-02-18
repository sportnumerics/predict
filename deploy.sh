set -ex

# check disk space
df -h

# for native compilation, gcc is not available unless we initialise lambci gcc
. ~/init/gcc
mkdir vendored/
mount -t tmpfs -o size=512m tmpfs vendored/
pip install -t vendored/ -r requirements.txt
npm install serverless

./decrypt.sh
source ./config/env.sh
unset AWS_SESSION_TOKEN

SLS_DEBUG=* node_modules/.bin/serverless deploy --stage=dev --verbose
