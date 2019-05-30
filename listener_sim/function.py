from __future__ import print_function
import sys
import os
import json
import pymysql
import bisect
import random
from datetime import datetime, timedelta

DATABASE = os.environ['DATABASE']
USER = os.environ['DB_USER']
PASSWD = os.environ['PASSWORD']
PORT = os.environ['PORT']
HOST = os.environ['HOST']
QUERY_MAX_ID = "select ifNull(max(event_id),0) as MAX_ID from Event"
QUERY_INSERT = "insert into Event(occurrence_timestamp) values(%s)"


def get_conn():
    try:
        print('Connect to DB: %s' % HOST)
        return pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE,  connect_timeout=5)
    except:
        print('Database Connection Failed: exception %s' % sys.exc_info()[1])
        return 'Failed'


def get_max_id(conn):
    print("getting max_id")

    try:
        # connect to Redshift and run the query
        cursor = conn.cursor()
        print(QUERY_MAX_ID)
        cursor.execute(QUERY_MAX_ID)
        result = cursor.fetchall()
        for row in result:
            eid = row[0]

        print("Latest Event Id: %s" % eid)
        cursor.close()

        print('Completed Successfully')
        return eid

    except:
        print('Query Failed: exception %s' % sys.exc_info()[1])
        return


def rand_event_count(hour):
    print("generating random event count")
    hours  = [6, 9, 12, 15, 17, 20, 22, 24]
    values = [0, 3, 6,  10, 20, 30, 10, 3]
    index = bisect.bisect_left(hours, hour)

    if index > 0:
        return random.randint(1, values[index])
    else:
        return values[index]


def get_new_rows(max_id, conn):
    # This function is a simulation that creates events
    # In a "normal" environment, it would be retrieving new event rows from a source
    # The source could be another database, events from an event bus or an API call to retrieve events
    print("getting new rows")
    rows = []
    if max_id == 0:
        latest_dt = datetime.now() - timedelta(seconds=30)
    else:
        cursor = conn.cursor()
        cursor.execute("select occurrence_timestamp from Event where event_id = %s", max_id)
        latest_dt = cursor.fetchall()[0][0] + timedelta(seconds=30)
        cursor.close()
    row = []

    for i in range(rand_event_count(latest_dt.hour)):
        row.append(latest_dt)
        rows.append(row)

    return rows


def insert_rows(rows, conn):
    print("inserting rows")
    cursor = conn.cursor()
    for row in rows:
        cursor.execute(QUERY_INSERT, row[0])
    conn.commit()
    cursor.close()
    return len(rows)


def log_env_vars():
    print("HOST: %s" % HOST)
    print("USER: %s" % USER)
    print("DATABASE: %s" % DATABASE)


def lambda_handler(event, context):
    print("listener_sim started")
    log_env_vars()

    conn = get_conn()
    max_id = get_max_id(conn)
    new_rows = get_new_rows(max_id,conn)
    count = insert_rows(new_rows, conn)
    conn.close()
    print("row_count: %s" % count)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "row_count": count
        }),
    }
