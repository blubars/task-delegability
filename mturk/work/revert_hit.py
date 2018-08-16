#!/usr/bin/env python3

#---------------------------------------------------------
# FILE DESCRIPTION:
#---------------------------------------------------------
# Download and save results from completed HIT assignments

#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
import boto3
import sys
import os.path

#---------------------------------------------------------
# GLOBALS
#---------------------------------------------------------
SINGLE_HIT_ID = '335HHSX8CDBO59MYR8G82VHMKMAHDE'

# CREDENTIALS NOTE:
# before using, set credentials either using the AWS CLI, or ~/.aws/credentials

# SANDBOX VS PRODUCTION
#endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
# Uncomment this line to use in production
endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

region_name = 'us-east-1'

client = boto3.client(
    'mturk',
    endpoint_url=endpoint_url,
    region_name=region_name,
)

#---------------------------------------------------------
# SCRIPT 
#---------------------------------------------------------
    
def process_hit(hit_id):
    print("=============================================")
    print(" - HIT [{}]".format(hit_id))
    try:
        client.update_hit_review_status(HITId=hit_id, Revert=True)
        print("    --> REVERTED (status->Reviewable)")
    except:
        print("    --> Failed?")
    print("---------------------------------------------")

def main():
    if len(sys.argv) < 2:
        print("Usage error: pass in a HIT id to revert (set status to Reviewable)")
        return
    else:
        hit_id = sys.argv[1]
        process_hit(hit_id)
        print("\nDone!")
    
if __name__ == "__main__":
    main()
