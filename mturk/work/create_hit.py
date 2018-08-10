#!/usr/bin/env python3

#---------------------------------------------------------
# FILE DESCRIPTION:
#---------------------------------------------------------
# Set up AMT HITs for task delegability survey

#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
import boto3
import sys
import csv

#---------------------------------------------------------
# GLOBALS
#---------------------------------------------------------
# file to save the output of hit creation status
STATUS_FILE_OUT = "created_hits.csv"
# file to read in HTMLQuestion form if that's how we're
# creating HITs. 
QUESTION_FILE_IN = "survey-question.xml"

LAYOUT_ID = '3VCL8E1RS172YYS1ULJJ4XMB571PS1'

# CREDENTIALS NOTE:
# before using, set credentials either using the AWS CLI, or ~/.aws/credentials

# SANDBOX VS PRODUCTION
endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
# Uncomment this line to use in production
# endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

region_name = 'us-east-1'

TITLE = "Should an AI do this task?"
DESCRIPTION = "Academic study about peoples' sentiments towards 'delegating' different kinds of tasks to an AI (artificial intelligence) versus to a person. You will consider one randomly-selected task (e.g., mowing a lawn), and provide your opinion in the form of a short survey. The survey will take approximately 5 minutes."
KEYWORDS = "AI, research, delegation, automation"
REWARD = "0.80"

client = boto3.client(
    'mturk',
    endpoint_url=endpoint_url,
    region_name=region_name,
)

#---------------------------------------------------------
# SCRIPT 
#---------------------------------------------------------

# 1. create HIT Type (template w/ metadata)
# 2. create HIT Layout (template for HIT w/ placeholder for input variables
# 3. create HITs, plug input data into layouts.

qualifications = [
# percentage of HITs approved
    {
        'QualificationTypeId': '000000000000000000L0',
        'Comparator': 'GreaterThanOrEqualTo',
        'IntegerValues': [
            99,
        ],
        'ActionsGuarded': 'PreviewAndAccept'
    },
    # number of HITs done
    {
        'QualificationTypeId': '00000000000000000040',
        'Comparator': 'GreaterThanOrEqualTo',
        'IntegerValues': [
            50,
        ],
        #'ActionsGuarded': 'PreviewAndAccept'
        'ActionsGuarded': 'Accept'
    },
    # worker's location
    {
        'QualificationTypeId': '00000000000000000071',
        'Comparator': 'EqualTo',
        'LocaleValues': [
            {
                'Country': 'US',
            },
        ],
        'ActionsGuarded': 'PreviewAndAccept'
    },
]

def create_hit_type():
    hitType = client.create_hit_type(
        AutoApprovalDelayInSeconds=172800, # 60s * 60m * 24hr * 2d = 
        AssignmentDurationInSeconds=1200, # 20m * 60s
        Reward=REWARD, # money paid to worker for HIT
        Title=TITLE, 
        Keywords=KEYWORDS,
        Description=DESCRIPTION,
        QualificationRequirements=[],
    )

    print("HIT Type Created! ID: {}".format(hitType['HITTypeId']))
    print("----------------------------------------")
    return hitType['HITTypeId']

def save_hit_create_response(response, annotation):
    with open(STATUS_FILE_OUT, 'a', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow([response['HIT']['HITId'], response['HIT']['CreationTime'], annotation, response['HIT']['Title'], response['HIT']['HITStatus'], response['HIT']['MaxAssignments']])
        
def create_hit_with_layout_id(index, hit_id, hit_params, layout_id):
    split_id = hit_params[0]['Value']
    print("[{}]: Creating HIT for split_id {}".format(index, split_id))
    # To avoid a fee, do not create a HIT with more than 10 assignments.
    response = client.create_hit_with_hit_type(
        HITTypeId=hit_id,
        MaxAssignments=2, # num times HIT can be accepted before unavailable
        LifetimeInSeconds=86400, # REQ: time after which HIT not available: 1 day
        #Question='string', # using HITLayoutID instead.
        RequesterAnnotation=split_id,
        #UniqueRequestToken='string',
        #AssignmentReviewPolicy={
        #HITReviewPolicy={
        HITLayoutId=layout_id,
        HITLayoutParameters=hit_params
    )
    save_hit_create_response(response, split_id)
    print("Done. HITId: {}\nCreationTime: \t{}\nTitle: \t{}\nDescription: \t{}\nKeywords:  \t{}\nHITStatus: \t{}\nAssignments: \t{}".format(response['HIT']['HITId'], response['HIT']['CreationTime'], response['HIT']['Title'], response['HIT']['Description'], response['HIT']['Keywords'], response['HIT']['HITStatus'], response['HIT']['MaxAssignments']))
    #print(response)
    print("----------------------------------------")

def create_hit_with_html_question(index, hit_id, hit_params):
    split_id = hit_params[0]['Value']
    print("[{}]: Creating HIT for split_id {}".format(index, split_id))
    
    # read the HTMLQuestion in from file
    with open(QUESTION_FILE_IN, 'r') as qfile:
        question = qfile.read()
    
        # To avoid a fee, do not create a HIT with more than 10 assignments.
        response = client.create_hit_with_hit_type(
            HITTypeId=hit_id,
            MaxAssignments=2, # num times HIT can be accepted before unavailable
            LifetimeInSeconds=86400, # REQ: time after which HIT not available: 1 day
            RequesterAnnotation=split_id,
            #UniqueRequestToken='string',
            #AssignmentReviewPolicy={
            #HITReviewPolicy={
            Question=question
        )
        save_hit_create_response(response, split_id)
        print("Done. HITId: {}\nCreationTime: \t{}\nTitle: \t{}\nDescription: \t{}\nKeywords:  \t{}\nHITStatus: \t{}\nAssignments: \t{}".format(response['HIT']['HITId'], response['HIT']['CreationTime'], response['HIT']['Title'], response['HIT']['Description'], response['HIT']['Keywords'], response['HIT']['HITStatus'], response['HIT']['MaxAssignments']))
        #print(response)
        print("----------------------------------------")
    
def main():
    # check if we passed an input file
    if len(sys.argv) < 2:
        print("Usage error: pass in an input file csv")
        return
    infile = sys.argv[1]
    with open(infile, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        # create HIT type, then create HITs according to input file.
        hit_id = create_hit_type()
        for i, row in enumerate(reader):
            hit_params = []
            for key, value in row.items():
                hit_params.append({'Name':key, 'Value':value})
            # iterate through input data, create HIT for each one.
            #create_hit_with_html_question(i, hit_id, hit_params)
            create_hit_with_layout_id(i, hit_id, hit_params, LAYOUT_ID) #'3ZWZ4MEZJXXQD14D3Z8UW2LYD111FQ')
    
if __name__ == "__main__":
    main()
