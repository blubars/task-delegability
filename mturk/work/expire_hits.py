#!/usr/bin/env python3

#---------------------------------------------------------
# FILE DESCRIPTION:
#---------------------------------------------------------
# Expire all active HITs.

#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
import boto3
import sys
import datetime

#---------------------------------------------------------
# GLOBALS
#---------------------------------------------------------

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
    
def expire_hit(hit, i):
    id = hit['HITId']
    #status = hit['HITStatus']
    annotation = hit['RequesterAnnotation']
    print("HIT [{}]: '{}' --> expired".format(i, id))
    res = client.update_expiration_for_hit(HITId=id, ExpireAt=datetime.datetime(2015, 1, 1))

def main():
    i = 0
    res = client.list_hits()
    while( res['NumResults'] > 0 ):
        print("Found {} reviewable HITs".format(res['NumResults']))
        for hit in res['HITs']:
            i += 1
            expire_hit(hit, i)
        res = client.list_hits(NextToken=res['NextToken'])
    print("\nDone! Processed {} HITs".format(i))
    
if __name__ == "__main__":
    main()
