#!/usr/bin/env python3

#---------------------------------------------------------
# FILE DESCRIPTION:
#---------------------------------------------------------
# List all of a Requester's HITs (except those deleted)

#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
import boto3
import sys

#---------------------------------------------------------
# GLOBALS
#---------------------------------------------------------
FILTER_ASSIGNMENTS = 0

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

def print_hits(index, page=None):
    if page is None:
        response = client.list_hits(MaxResults=20)
    else:
        response = client.list_hits(NextToken=page, MaxResults=20)
    length = response['NumResults']
    if length == 0:
        print("-------------------------------------------------")
        print("No more HITs found. Total: {}".format(index))
        return None, index
    next = response['NextToken']
    print("-------------------------------------------------")
    print("Retrieved {} results; NextPage={}".format(length, next))
    for i in range(length):
        completed = response['HITs'][i]['NumberOfAssignmentsCompleted']
        if FILTER_ASSIGNMENTS > 0 and FILTER_ASSIGNMENTS == completed:
            continue
        print("-------------------------------------------------")
        print(" INDEX {}".format(index))
        print("-------------------------------------------------")
        print("HIT ID: \t{}".format(response['HITs'][i]['HITId']))
        print("Title:  \t{}".format(response['HITs'][i]['Title']))
        print("SplitId: \t{}".format(response['HITs'][i]['RequesterAnnotation']))
        print("Status: \t{}".format(response['HITs'][i]['HITStatus']))
        print("Assignments Avail/Pend/Complete: \t{}/{}/{}".format(response['HITs'][i]['NumberOfAssignmentsAvailable'], response['HITs'][i]['NumberOfAssignmentsPending'], completed))
        index += 1
    return next, index

if len(sys.argv) >= 2:
    try:
        FILTER_ASSIGNMENTS = int(sys.argv[1])
        print("Showing filtered (incomplete) HIT results only")
    except ValueError:
        print("To filter by incomplete HITs, pass in # of assignments expected")
    
print("Active HITs:")
next, index = print_hits(0)
while next != None:
    next, index = print_hits(index, next)
print("-------------------------------------------------\nDone.")
