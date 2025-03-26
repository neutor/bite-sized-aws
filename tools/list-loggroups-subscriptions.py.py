#!/usr/bin/env python3
# Developed by Max Kimstach

# Get csv file with all log groups and subscription filters across all accounts in AWS Organisation 
# ./log-groups-report saveDirectory

# ToDo: Regions

import boto3
import csv
import os
import sys
import json
from pathlib import Path

root_profile = 'finance'
region = 'ap-southeast-2'

def get_session(account):
    if account['Id'] == root_acc_id:
        return root_session
    role_arn = 'arn:aws:iam::' + account['Id'] + ':role/OrganizationAccountAccessRole'
    sts = root_session.client('sts')
    creds = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName='something')['Credentials']
    session = boto3.session.Session(
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretAccessKey'],
        aws_session_token=creds['SessionToken'])
    return session

def paginator(client, command, args={}):
    resources = []
    paginator = client.get_paginator(command)
    results = paginator.paginate(**args).result_key_iters()
    return list(results[0])

def get_log_groups():
    print('Starting')
    logs = session.client('logs', region_name=region)
    log_groups = paginator(logs, 'describe_log_groups')
    for group in log_groups:
        lg_name = group['logGroupName']
        filters = logs.describe_subscription_filters(logGroupName=lg_name)['subscriptionFilters']
        if filters:
            csv_writer.writerow([ acc_alias, lg_name, filters[0]['destinationArn'], filters[0]['filterName'] ])


if __name__ == '__main__':

    results_dir = sys.argv[1]
    root_session = boto3.session.Session(profile_name=root_profile)
    root_acc_id = root_session.client('sts').get_caller_identity().get('Account')
    orgs = root_session.client('organizations')
    accounts = [a for a in orgs.list_accounts()['Accounts'] if a['Status'] == 'ACTIVE']

    Path(results_dir).mkdir(parents=True, exist_ok=True)
    file = open(os.path.join(results_dir, 'log_groups.csv'), mode='w')
    csv_writer = csv.writer(file, delimiter=',')
    csv_writer.writerow(['Account', 'DNS Name', 'Type', 'Value'])

    cfds = []
    for account in accounts: 
        session = get_session(account)
        acc_alias = session.client('iam').list_account_aliases()['AccountAliases'][0]
        print(acc_alias)
        get_log_groups() 
    file.close()