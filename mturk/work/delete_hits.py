#!/usr/bin/env python3

#---------------------------------------------------------
# FILE DESCRIPTION:
#---------------------------------------------------------# 
# Delete HITs. Deletes all HITs in the Reviewable state.

#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
import boto3
import sys

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
def delete_hits(page=None):
    if page is None:
        response = client.list_hits(MaxResults=100)
    else:
        response = client.list_hits(NextToken=page, MaxResults=100)
    next = response['NextToken']
    length = response['NumResults']
    print("-------------------------------------------------")
    print("Retrieved {} results; NextPage={}".format(length, next))
    for i in range(length):
        id = response['HITs'][i]['HITId']
        print("-------------------------------------------------")
        print(" INDEX {}".format(i))
        print("-------------------------------------------------")
        print("HIT ID: \t{}".format(id))
        print("Title:  \t{}".format(response['HITs'][i]['Title']))
        print("SplitId: \t{}".format(response['HITs'][i]['RequesterAnnotation']))
        print("Status: \t{}".format(response['HITs'][i]['HITStatus']))
        print("Review status: \t{}".format(response['HITs'][i]['HITReviewStatus']))
        print("Assignments Avail/Pend/Complete: \t{}/{}/{}".format(response['HITs'][i]['NumberOfAssignmentsAvailable'], response['HITs'][i]['NumberOfAssignmentsPending'], response['HITs'][i]['NumberOfAssignmentsCompleted']))
        try:
            del_resp = client.delete_hit(HITId=id)
            print("DELETED SUCCESSFULLY")
        except:
            print("FAILED TO DELETE: {}".format(sys.exc_info()[0]))
    return next

print("Deleting HITs...")
next = delete_hits()
print("-------------------------------------------------\nDone.")
