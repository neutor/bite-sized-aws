# Bite-sized AWS - simple but useful templates for common things


## List

Most folders are standalone Cloudformation template to deploy the thing or a single python script to do the task.

The template has Parameters you need to fill. Go to AWS Console / Cloudformation and press "Create Stack". Use "new resources" and "upload template". 

The script will have some default settings to set before running. You need to setup your AWS CLI with profile(s), even if it is a single account.

-  /static-s3-website    Static website in S3 with Cloudfront for custom domain name and HTTPS
-  /vpc                  Typical AWS VPC, 3 AZs by 3 layers, suitable for most projects
-  /tools                Python script to do one specific task. Uses Boto3 to talk to AWS