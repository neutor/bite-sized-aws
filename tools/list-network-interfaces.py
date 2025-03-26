#!/usr/bin/env python3

# Developed by Max Kimstach
# Usage: 
# ./nifs.py myendpoints.csv 


# ToDo:
# switch to assume OrgRole for each account

import boto3
import json
import sys
import re
import csv
import datetime
from dateutil.tz import *
from botocore.config import Config


config = Config( retries = dict(max_attempts = 10) )

def paginator(client, command, args={}):
    resources = []
    paginator = client.get_paginator(command)
    results = paginator.paginate(**args).result_key_iters()
    return list(results[0])

def r53_records(acc_id, client, dns_name):
    if not zones.get(acc_id):
        zones[acc_id] = client.list_hosted_zones()['HostedZones']
        for zone in zones[acc_id]:
            rrsets = client.list_resource_record_sets(HostedZoneId=zone['Id'])['ResourceRecordSets']
            zone['ResourceRecordSets'] = rrsets
    for zone in zones[acc_id]:
        for rrset in zone['ResourceRecordSets']:
            if rrset.get('ResourceRecords'):
                for rr in rrset['ResourceRecords']:
                    if rr['Value'].rstrip('.') == dns_name:
                        return rrset['Name'].rstrip('.')
            if rrset.get('AliasTarget'):
                name = rrset['AliasTarget']['DNSName'].replace('dualstack.', '').rstrip('.')
                if name == dns_name:
                    return rrset['Name'].rstrip('.')
    return dns_name.rstrip('.')

def list_sec(session, regions, acc_alias, acc_id, csv_writer):
    r53 = session.client('route53')
    for region in regions:
        elbv1 = session.client('elb', region_name=region)
        elbv2 = session.client('elbv2', region_name=region)
        elbsv1 = paginator(elbv1, 'describe_load_balancers')
        elbs = list(map(lambda x: (x, 'v1'), elbsv1))
        elbsv2 = paginator(elbv2, 'describe_load_balancers')
        elbs.extend( list(map(lambda x: (x, 'v2'), elbsv2)) )
        ec2 = session.client('ec2', region_name=region)
        reservations = paginator(ec2, 'describe_instances')
        instances = [i for r in reservations for i in r['Instances']]
        print(region)
        owners = []
        ec2 = session.client('ec2', region_name=region)
        nifs = paginator(ec2, 'describe_network_interfaces')
        for nif in nifs:
            pub_ip = None
            try:
                pub_ip = nif['Association']['PublicIp']
            except KeyError:
                try:
                    pub_ip = [p['Association']['PublicIp'] for p in nif['PrivateIpAddresses']][0]
                except KeyError:
                    pass
            if pub_ip:
                if nif['InterfaceType'] == 'nat_gateway':
                    continue
                instance_id = nif['Attachment'].get('InstanceId')
                if not instance_id:
                    owner_id = nif['Attachment'].get('InstanceOwnerId')
                    if owner_id == 'amazon-elb':
                        elb_name = elb_descr_to_name(nif['Description'])
                        owner = elb_name
                        elb = [lb for lb in elbs if lb[0]['LoadBalancerName'] == elb_name][0]
                        if elb[1] == 'v2':
                            arn = 'arn:aws:elasticloadbalancing:' + region + ':' + acc_id + ':loadbalancer/' + nif['Description'][4:]
                            tagds = elbv2.describe_tags(ResourceArns=[arn])
                        else:
                            tagds = elbv1.describe_tags(LoadBalancerNames=[elb_name])
                        name = get_name_tag(tagds['TagDescriptions'][0])
                        pub_ip = elb[0]['DNSName']
                    else:
                        owner = owner_id
                        name = ''
                else:
                    owner = instance_id
                    instance = [i for i in instances if i['InstanceId'] == instance_id][0]
                    name = get_name_tag(instance)
                secgroup_ids = [sg['GroupId'] for sg in nif['Groups']]
                issafe = safe_sgroups(ec2, secgroup_ids)
                if owner not in owners:  # if not issafe[0] and owner not in owners:
                    dns_name = r53_records(acc_id, r53, pub_ip)
                    owners.append(owner)
                csv_writer.writerow([ acc_alias, region, pub_ip, dns_name, issafe, ports ])

def elb_descr_to_name(descr):
    stripped = descr[4:].split('/')  # exclude 'ELB ' prefix
    if stripped[0] == 'app':
        return stripped[1]
    return stripped[0]

def get_name_tag(resource):
    name = ''
    if resource.get('Tags'):
        for tag in resource.get('Tags'):
            if tag['Key'] == 'Name':
                name = tag['Value']
                break
    return name


if __name__ == '__main__':

    filename = sys.argv[1]
    file = open(filename, mode='w')
    csv_writer = csv.writer(file, delimiter=',')
    csv_writer.writerow(['Account','Region', 'PublicIP', 'DNSName', 'Safe', 'Ports', 'EC2/ELB', 'SecGroup', 'Name'])

    profiles = ['prod', 'uat', 'dev', 'service', 'sandbox', 'finance', 'brandtology']
    for profile in profiles:
        print(profile)
        session = boto3.session.Session(profile_name=profile)
        ec2 = session.client('ec2')
        regions = ['ap-southeast-1', 'ap-southeast-2']
        acc_alias = session.client('iam').list_account_aliases()['AccountAliases'][0]
        acc_id = session.client('sts').get_caller_identity().get('Account')

        list_sec(session, regions, acc_alias, acc_id, csv_writer)


            


