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
def check_assignments_all_approved(hit):
    # return TRUE if all approved, FALSE if any rejected
    res = client.list_assignments_for_hit(HITId=hit['HITId'], AssignmentStatuses=['Submitted', 'Approved', 'Rejected'])
    for i, assign in enumerate(res['Assignments']):
        if assign['AssignmentStatus'] != "Approved":
            return False
    return True
        

def delete_hits(page=None):
    if page is None:
        response = client.list_hits(MaxResults=20)
    else:
        response = client.list_hits(NextToken=page, MaxResults=20)
    next = response['NextToken']
    length = response['NumResults']
    print("-------------------------------------------------")
    print("Retrieved {} results; NextPage={}".format(length, next))
    for i in range(length):
        hit = response['HITs'][i]
        id = hit['HITId']
        print("-------------------------------------------------")
        print(" INDEX {}".format(i))
        print("-------------------------------------------------")
        print("  HIT ID: \t{}".format(id))
        print("  Title:  \t{}".format(hit['Title']))
        print("  SplitId: \t{}".format(hit['RequesterAnnotation']))
        print("  Status: \t{}".format(hit['HITStatus']))
        print("  Assignments Avail/Pend/Complete: \t{}/{}/{}".format(hit['NumberOfAssignmentsAvailable'], hit['NumberOfAssignmentsPending'], hit['NumberOfAssignmentsCompleted']))
        delete_this = check_assignments_all_approved(hit)
        if delete_this:
            try:
                del_resp = client.delete_hit(HITId=id)
                print("    --> DELETED SUCCESSFULLY")
            except:
                print("    --> FAILED TO DELETE: {}".format(sys.exc_info()[0]))
        else:
            print("    --> SKIPPING, SOME ASSIGN NOT APPROVED")
    return next, length

print("Deleting HITs...")
next, len = delete_hits()
#while(next != None or len > 0):
#    next, len = delete_hits(next)
print("-------------------------------------------------\nDone.")
