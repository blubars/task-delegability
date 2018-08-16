#!/usr/bin/env python3

#---------------------------------------------------------
# FILE DESCRIPTION:
#---------------------------------------------------------
# Approve a previously-rejected assignment

#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
import boto3
import sys
import os.path
import csv

#---------------------------------------------------------
# GLOBALS
#---------------------------------------------------------
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

def main():
    # check if we passed an input file
    if len(sys.argv) < 2:
        print("Usage error: pass in an input file csv containing Assignments to approve")
        return
    infile = sys.argv[1]
    with open(infile, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        i = 0
        for row in reader:
            id = row['assign id']
            try:
                # TODO: should check assignment status to see if in 'Submitted' state.
                print("[{}] Approving AssignmentID '{}'".format(i, id))
                res = client.approve_assignment(AssignmentId=id, RequesterFeedback="Thank you!", OverrideRejection=True)
                #print(res)
                print("   --> Approved!")
            except:
                # not really a safe assumption. really should check the status or the exception
                print("   --> Failed. Already approved?")
            i += 1
        print("\nDone! Processed {} HITs".format(i))
    
if __name__ == "__main__":
    main()
