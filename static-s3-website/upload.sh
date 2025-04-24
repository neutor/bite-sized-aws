#!/usr/bin/env bash

hugo

aws s3 sync ./public/ s3://your-s3-bucket-name/ --sse --delete --exclude '.DS_Store'

aws cloudfront create-invalidation --distribution-id '<your-CF-Distribution-Id>' --paths '/*'