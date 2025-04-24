# Secure static website hosting in AWS S3 with CloudFront


This template creates AWS infrastructure needed to host a static website. The helper Bash script is an example of publishing the website content from local machine.

## Features:

- SSL Certificate, HTTPS
- Custom Domain name
- One click deployment using AWS Console and any browser
- A CloudFront Function to append /index.html - fixes CloudFront errors with clean (tidy) website links

## Deployment

1. Login to AWS Console, go Cloudformation (CFN) / Stacks / Create Stack
2. Upload the Template from file, fill the parameters of the CFN template, each has a Description to help you
3. Proceed to create the Stack, wait till Stack creation is complete.
4. Write down the value of DistributionId in Stack Outputs in AWS Console. 


## Publishing website content

1. Setup AWS CLI on your local machine
2. Modify `upload.sh` script - add your CloudFront DistributionId (step 4 above) to the cache clearing command.
3. replace `./public/` with your path to static website folder on your machine.
4. Run the `upload.sh` script