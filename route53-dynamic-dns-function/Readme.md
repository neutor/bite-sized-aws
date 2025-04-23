# Dynamic DNS with Route53 using AWS Lambda function invoked with simple HTTPS request.

If you host your domain in AWS Route53, and need Dynamic DNS, this solution is for you. By using only AWS and a plain HTTPS request with new IP address as URL query string parameter, this function will update your DNS record with your new IP.

The provided CloudFormation template is all is needed to deploy the solution. Later I will include the script for Mikrotik routers/switches with RouterOS, that periodically invokes the function with its latest public IP address, but you can use anything, like Linux cron job, from any system, to do the updates. 

## Why

I needed Dynamic DNS feature working with DNS hosted in AWS Route53. It should be invoked using simple HTTPS GET request with parameters, as my router cannot do request signing due to hardware limitations.

Heavy lifting work of updating the Route53 record is in the Lambda function, deployed in AWS and invoked by the RouterOS using the `/tool fetch` command from above. The function uses Boto3 Python library to interact with AWS Route53 APIs.

The HTTPS request that the switch (RouterOS) fires periodically looks like this:

`GET https://hjgytyt34hd21jg34hg5kjh7j8hjh3hg.lambda-url.ap-southeast-2.on.aws/?newip=123.12.12.12&secret=hellokitty`

The Lambda function has a "Function URL" property configured, which allows it to be invoked (executed) by plain, unsigned HTTPS request. Once invoked, it gets the IP from the request's URL parameters and updates the DNS record in Route53 if IP has changed.



## Deployment

Lambda "Function URLs" are not supported in all AWS Regions. Please check https://docs.aws.amazon.com/lambda/latest/dg/urls-invocation.html

1. Login to AWS Console, go Cloudformation (CFN) / Stacks / Create Stack
2. Upload the Template from file, fill the three parameters of the CFN template, each has a Description to help you
3. Create the CFN stack. Go to the Outputs tab of the stack, copy the value of "FunctionUrl" output
4. Check it is working. In your terminal:

`curl 'https://<function url>/?newip=123.12.12.12&secret=<your secret>'`

You should get 'OK' and IP updated in Route53. 

## Security

The Function URL is publicly accessible and there is no authentication. The reason is my switch does not have the capacity to run a Python app to SigV4-sign the request with AWS IAM User credentials. The right way is to sign the request with AWS IAM credentials and set "AuthType = AWS_IAM" instead on NONE in Function URL settings, but this cannot be done on CRS309 due to hardware limitations.

The mitigation is two-fold:
* The AWS-generated Function URL contains random 32 alphanumerical URL prefix and is impossible to guess or brute-force. But it is still exposed in [SSL SNI](https://en.wikipedia.org/wiki/Server_Name_Indication), your ISP might get it.
* Use of the `secret` URL parameter, as an additional measure. This, IMHO, is safe from SNI inspection by intermediate boxes.

Obviously, this is not Enterprise solution, I aim it at home users.


#### Use in Mikrotik switches and routers (work in progress)

I have a Mikrotik switch, CRS309, which runs RouterOS firmware. I use it, additionally, as a basic home router, with Firewall rules, NAT and VLANs.

Mikrotik offers its own Dynamic DNS service, but it does not work with AWS R53. RouterOS has a basic scripting abilities, and for heavy stuff like python you can use [Containers](https://help.mikrotik.com/docs/spaces/ROS/pages/84901929/Container), but not on my switch, which has only 16MB of flash storage, already 80% full. My switch does not even have a USB port.

But RouterOS does have three things that will make Dynamic DNS feature work on my switch:
* `/tool fetch` command. This fires a simple HTTP request to any URL
* `/system scheduler` like a cron in Linux, invokes a script periodically
* `/system script` adds simple, lightweight script to the RouterOS

Sequence of events:
* RouterOS Scheduler starts the "ddns-route53" script every 10 minutes
* "ddns-route53" script finds the WAN interface public IP address and sends it in HTTPS request to Lambda function
* Lambda function checks if the IP address is different from the one in Route53 and updates it



### To Do:
* Sanitize request values 
* IPV6 (AAAA record type) support

