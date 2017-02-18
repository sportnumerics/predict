#!/bin/bash

./decrypt.sh
source ./config/env.sh
unset AWS_SESSION_TOKEN

SLS_DEBUG=* sls deploy --stage=dev --verbose
