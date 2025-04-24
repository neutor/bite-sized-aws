# Bite-sized AWS - simple but useful templates for common things

Handcrafted with love CloudFormation templates and Python apps for simple, standalone tasks. Idea is similar to concept of the Unix philosophy - "Do one thing and do it well."

Most folders are standalone Cloudformation templates to deploy the thing or a single python script to do the task.

The template has Parameters you need to fill. Go to AWS Console / Cloudformation and press "Create Stack". Use "new resources" and "upload template". 

The scripts may have some default settings, change it before running. You need to have AWS CLI configured with credentials.


## [static-s3-website](static-s3-website)

Static website in S3 with Cloudfront for custom domain name and HTTPS


## vpc

Typical AWS VPC, 3 AZs by 3 layers, suitable for most projects


## route53-dynamic-dns-function

Dynamic DNS with Route53 using AWS Lambda function invoked with simple HTTPS request.


## tools

Python script to do one specific task. Uses Boto3 to talk to AWS