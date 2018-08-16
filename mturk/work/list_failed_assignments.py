#!/usr/bin/env python3

#---------------------------------------------------------
# FILE DESCRIPTION:
#---------------------------------------------------------
# Generate CSV list of assignments that were failed, and
# need to be re-run.
# INPUT: CSV results file with failed rows marked "no" in
#   the "approved" column.
# OUTPUT: CSV list of split_ids to run again, single 
#   assignment.

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
CSV_OUT_FILE = "failed-assignments.csv"

#---------------------------------------------------------
# SCRIPT 
#---------------------------------------------------------

def main():
    global CSV_OUT_FILE
    if len(sys.argv) < 2:
        print("Please pass in a result CSV file to process")
        return
        
    CSV_IN_FILE = sys.argv[1]
    i = 0
    with open(CSV_IN_FILE, newline='') as csvfile_in:
        reader = csv.DictReader(csvfile_in)
        with open(CSV_OUT_FILE, 'w', newline='') as csvfile_out:
            writer = csv.DictWriter(csvfile_out, fieldnames=['split_id', 'assign id'])
            writer.writeheader()
            for i, row in enumerate(reader):
                if row['approved'] == "no":
                    # save rejected row in output file
                    outrow = {
                        'split_id':row['Annotation'], 
                        'assign id':row['assign id'] }
                    writer.writerow(outrow)
        print("\nDone! Processed {} assignments".format(i+1))
    
if __name__ == "__main__":
    main()
