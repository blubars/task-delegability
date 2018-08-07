#!/usr/bin/env python3

# FILE DESCRIPTION
# This is a script to take an input (a csv listing tasks)
# and output a sqlite database.

import sys
import csv
import sqlite3

if len(sys.argv) < 2:
    print("Error: missing the task CSV file name")
    sys.exit()

# Set up database.
# Delete db if it exists, create a new one
conn = sqlite3.connect('task-list.db')
c = conn.cursor()
# create table
try:
    c.execute("DROP TABLE tasks")
except sqlite3.OperationalError:
    pass
c.execute("CREATE TABLE tasks (id integer, task text)")

# read CSV and transfer into DB
with open(sys.argv[1], newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for i,row in enumerate(reader):
        task = row['Task description']
        # save task into the db
        cmd = "INSERT INTO tasks VALUES (" + str(i + 1) + ", \"" + task + "\")"
        c.execute(cmd)
    conn.commit()

conn.close()

