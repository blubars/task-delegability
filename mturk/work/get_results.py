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
import csv
import xml.etree.ElementTree as ET

#---------------------------------------------------------
# GLOBALS
#---------------------------------------------------------
PROCESS_EXPERT = True

CSV_OUT_PATH = "."
CSV_OUT_FILE = "results.csv"
AUTOAPPROVE = False

if PROCESS_EXPERT:
    #HIT_TYPE_ID = '38E1HBOA1QLK36TU6K3OURXX73X80R'
    # [EXPERT] CSV column names
    FIELDNAMES = ['HIT id', 'Annotation', 'Worker id', 'assign id', 'accept time', 'submit time', 'gender', 'gender-input', 'age', 'tech-level', 'edu-level', 'l-social-skills','l-creativity','l-effort','sanity-check1','l-expertise','l-abilities','l-accountable','l-uncertainty','l-impact','sanity-check2','l-trust','l-process','l-values', 'label']
else:
    #HIT_TYPE_ID = '38E1HBOA1QLK36TU6K3OURXX73X80R'
    # [PERSONAL] CSV column names
    FIELDNAMES = ['HIT id', 'Annotation', 'Worker id', 'assign id', 'accept time', 'submit time', 'gender', 'gender-input', 'age', 'tech-level', 'edu-level', 'l-social-skills','l-creativity','l-effort','sanity-check1','l-expertise','l-abilities','l-accountable','l-uncertainty','l-impact','l-intrinsic','l-learning','l-important','sanity-check2','l-trust','l-process','l-values', 'label']

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

def process_assignment(csvwriter, HITId, annotation, assignment):
    assign_id = assignment['AssignmentId']
    acceptTime = assignment['AcceptTime']
    submitTime = assignment['SubmitTime']
    #result_row = [HITId, annotation, assignment['WorkerId'], assign_id, acceptTime, submitTime]
    result_row = {
        'HIT id': HITId, 
        'Annotation': annotation, 
        'Worker id': assignment['WorkerId'], 
        'assign id': assign_id, 
        'accept time': acceptTime, 
        'submit time': submitTime }
    root = ET.fromstring(assignment['Answer'])
    namespaces = {'ns': 'http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionFormAnswers.xsd'}
    #for q_num, elem in enumerate(root.iterfind("Answer")):
    for q_num, elem in enumerate(root.findall("ns:Answer", namespaces)):
        q_id = elem.find("ns:QuestionIdentifier", namespaces).text
        q_resp = elem.find("ns:FreeText", namespaces).text
        print("  - [Q{}] {}: {}".format(q_num, q_id, q_resp))
        result_row[q_id] = q_resp
    csvwriter.writerow(result_row)
    if AUTOAPPROVE:
        print("   --> Assignment Approved.")
        client.approve_assignment(AssignmentId=assign_id, RequesterFeedback="Thank you!")
    
def process_hit(csvwriter, hit, i):
    id = hit['HITId']
    annotation = hit['RequesterAnnotation']
    print("=============================================")
    print("PROCESSING HIT [{}]: {}".format(i, id))
    print("  annotation: {}".format(annotation))
    res = client.list_assignments_for_hit(HITId=id, AssignmentStatuses=['Submitted'])
    try:
        client.update_hit_review_status(HITId=id, Revert=False)
    except:
        pass
    for i, assign in enumerate(res['Assignments']):
        print("  ---------------------------------------------")
        print("  ASSIGN [{}] ID={}:".format(i, assign['AssignmentId']))
        process_assignment(csvwriter, id, annotation, assign)
    #print("---------------------------------------------")

def main():
    global CSV_OUT_PATH
    global CSV_OUT_FILE
    global FIELDNAMES
    if len(sys.argv) >= 2:
        # if a directory, use def filename in that dir.
        if os.path.isdir(sys.argv[1]):
            CSV_OUT_PATH = sys.argv[1]
            CSV_OUT_FILE = os.path.join(CSV_OUT_PATH, CSV_OUT_FILE)
        else:
            CSV_OUT_FILE = os.path.normpath(sys.argv[1])
    # check if we passed an input file
    isblank = os.path.isfile(CSV_OUT_FILE)
    with open(CSV_OUT_FILE, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        if not isblank:
            writer.writeheader()
            #writer.writerow(['HIT id', 'Annotation', 'Worker id', 'assign id', 'accept time', 'submit time', 'gender', 'gender-input', 'age', 'tech-level', 'edu-level', 'l-social-skills','l-creativity','l-effort','sanity-check1','l-expertise','l-abilities','l-accountable','l-uncertainty','l-impact','l-intrinsic','l-learning','l-important','sanity-check2','l-trust','l-process','l-values', 'label'])
        i = 0
        res = client.list_reviewable_hits(Status='Reviewable')
        #res = client.list_reviewable_hits(HITTypeId=HIT_TYPE_ID, Status='Reviewable')
        while( res['NumResults'] > 0 ):
            print("Found {} reviewable HITs".format(res['NumResults']))
            for hit in res['HITs']:
                i += 1
                if PROCESS_EXPERT:
                    if "expert" in hit['Title']:
                        process_hit(writer, hit, i)
                else:
                    if "expert" not in hit['Title']:
                        process_hit(writer, hit, i)
            res = client.list_reviewable_hits(Status='Reviewable', NextToken=res['NextToken'])
        print("\nDone! Processed {} HITs".format(i))
    
if __name__ == "__main__":
    main()
