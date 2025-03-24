# Generic three layer, multi AZ VPC

This is the generic VPC template with Internet Gateway for Public subnets.  
It creates three level structure across two or, optionally, three Availability zones, with 6 or 9 Subnets, per level Route Tables, NAT Gateways and Private subnets ACLs.  
NAT Gateways are optional but you want them to allow software installs and updates from internet via NAT.  


## VPC Structure

VPC is segmented using Subnets, for separation of logical services.
Level 1 subnets, `public-a`, `public-b` are public, with public traffic routed through an Internet Gateway. All systems in these subnets either Load Balancers (ELBs) or Proxy servers with elastic IP addresses for inbound traffic.

The level 2 subnets, `private-a`, `private-b`, have no direct inbound access from the Internet. If NAT Gateways are deployed, level 2, `private` subnets are given a route to NAT Gateway EIP. It means that outbound access to internet is via NAT GWs. Still there is no inbound access from internet.

Level 2 subnets, `private` subnets,  are for computing hosts (EC2), like web servers and application servers, queue processors, reporting systems, or any other application that does not require direct connectivity from users. Private subnets are associated with route table without route to Internet Gateway.  
Template creates NAT Gateways in every public subnet, and private subnets will have 0.0.0.0/0 routed to NAT GW EIPs. It is optional, CreateNatGWs parameter can be set to false.

The level 3 subnets, `restricted-a`, `restricted-b`, have neither outbound nor inbound access to Internet.

Level 3 subnets, `restricted`, are for persistence stores: databases, cache clusters, data pipelines.
These subnets are allowed access only from and to level 2, `private` subnets of the same vpc stack (same environment), using ACLs, applied to them. This feature exists in `-menv` template.

Additional security is achieved by using Security Groups, which are Not part of this template, and must be created and configured in application stacks.

## Using VPC outputs in other stacks

As this template outputs are also exported as StackName-public-a and the like, it is convenient to use the stack's outputs in other stacks. Add the following to your application stack:
```
  "Parameters" : {

    "VpcStackName": {
      "Description": "Name of existing VPC stack",
      "Type": "String"
    },
...

  "Resources": {
    "ElasticLoadBalancer" : {
      "Type" : "AWS::ElasticLoadBalancing::LoadBalancer",
      "Properties" : {
        "Subnets" : [
          { "Fn::ImportValue" : {"Fn::Sub": "${VpcStackName}-public-a" } },
          { "Fn::ImportValue" : {"Fn::Sub": "${VpcStackName}-public-b" } }
        ],
...
```