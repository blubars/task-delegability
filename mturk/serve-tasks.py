#!/usr/bin/env python3

#---------------------------------------------------------
# FILE DESCRIPTION:
#---------------------------------------------------------
# This program responds to AJAX requests containing
# the task ID. It will retrieve the task from the database
# and send the text in an HTTP response.

#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
#import sys
#import http.server
from wsgiref.simple_server import make_server, demo_app
from cgi import parse_qs, escape
import sqlite3

#---------------------------------------------------------
# GLOBALS
#---------------------------------------------------------
dbfile = 'db/task-list.db'

#---------------------------------------------------------
# SCRIPT 
#---------------------------------------------------------
# WSGI application
def application(environ, start_response):
    task = None
    #setup_testing_defaults(environ)
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    query = parse_qs(environ['QUERY_STRING'])
    rawids = query.get('t', ['']) # get 1st query, should be only 1
    # error check: should have an ID. 
    if len(rawids) > 0:
        taskid = escape(rawids[0])

        # open a connection to the database
        conn = sqlite3.connect(dbfile)
        c = conn.cursor()
        t = (taskid,)
        c.execute('SELECT task FROM tasks WHERE id=?', t)
        task = c.fetchone()
        if task is not None:
            task = task[0]
        conn.close()

    if task is None:
        task = "ERROR!"
    print(task)
    #ret = [("%s: %s\n" % (key, value)).encode("utf-8")
    #       for key, value in environ.items()]
    ret =  [task.encode("utf-8")]
    return ret

def main():

    # run the server
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()

if __name__ == "__main__":
    main()

