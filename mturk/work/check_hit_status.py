#!/usr/bin/env python3

#---------------------------------------------------------
# FILE DESCRIPTION:
#---------------------------------------------------------
# List all of a Requester's HITs (except those deleted)

#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
import boto3

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

def print_hits(page=None):
    if page is None:
        response = client.list_hits(MaxResults=20)
    else:
        response = client.list_hits(NextToken=page, MaxResults=20)
    length = response['NumResults']
    if length == 0:
        print("No HITs found.")
        return None
    next = response['NextToken']
    print("-------------------------------------------------")
    print("Retrieved {} results; NextPage={}".format(length, next))
    for i in range(length):
        print("-------------------------------------------------")
        print(" INDEX {}".format(i))
        print("-------------------------------------------------")
        print("HIT ID: \t{}".format(response['HITs'][i]['HITId']))
        print("Title:  \t{}".format(response['HITs'][i]['Title']))
        print("SplitId: \t{}".format(response['HITs'][i]['RequesterAnnotation']))
        print("Status: \t{}".format(response['HITs'][i]['HITStatus']))
        print("Review status: \t{}".format(response['HITs'][i]['HITReviewStatus']))
        print("Assignments Avail/Pend/Complete: \t{}/{}/{}".format(response['HITs'][i]['NumberOfAssignmentsAvailable'], response['HITs'][i]['NumberOfAssignmentsPending'], response['HITs'][i]['NumberOfAssignmentsCompleted']))
    return next

print("Active HITs:")
next = print_hits()
while next != None:
    next = print_hits(next)
print("-------------------------------------------------\nDone.")
