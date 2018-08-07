#!/usr/bin/env python3

#---------------------------------------------------------
# FILE DESCRIPTION:
#---------------------------------------------------------
# Check the balance in the AMT AWS account. Good for using to
# sanity check the connection and credentials.

#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
import boto3

# CREDENTIALS NOTE:
# before using, set credentials either using the AWS CLI, or ~/.aws/credentials

# SANDBOX VS PRODUCTION
endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
# Uncomment this line to use in production
# endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

region_name = 'us-east-1'

client = boto3.client(
    'mturk',
    endpoint_url=endpoint_url,
    region_name=region_name,
)

#---------------------------------------------------------
# SCRIPT 
#---------------------------------------------------------

# This will return $10,000.00 in the MTurk Developer Sandbox
print(client.get_account_balance()['AvailableBalance'])