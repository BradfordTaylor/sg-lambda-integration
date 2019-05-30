from __future__ import print_function
import sys
import os
import json
import pymysql
from datetime import datetime


DATABASE = os.environ['DATABASE']
USER = os.environ['DB_USER']
PASSWD = os.environ['PASSWORD']
PORT = os.environ['PORT']
HOST = os.environ['HOST']
BUCKET = os.environ["S3_BUCKET"]
QUERY_EXPORT = "select DATE_FORMAT(dt_bucket,\"%Y-%m-%d %H:%i:%s\"), actual_count from EventCount " \
               "where dt_bucket > DATE_SUB(NOW(),INTERVAL 1 YEAR)\n" \
               "into outfile S3 %s\n" \
               "fields terminated by ','\n" \
               "lines terminated by '\\r'" \
               "OVERWRITE ON"


def get_conn():
    try:
        print('Connect to DB: %s' % HOST)
        return pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE,  connect_timeout=5)
    except:
        print('Database Connection Failed: exception %s' % sys.exc_info()[1])
        return 'Failed'


def export_event_count(conn):
    print("Exporting last year of EventCount data")
    dt = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    s3_bucket = "s3://%s/export/EventCount-%s.csv" % (BUCKET, dt)
    print("S3 Bucket: %s" % s3_bucket)

    cursor = conn.cursor()
    cursor.execute(QUERY_EXPORT, s3_bucket)
    rowcount = cursor.rowcount
    cursor.close()
    return rowcount


def log_env_vars():
    print("HOST: %s" % HOST)
    print("USER: %s" % USER)
    print("DATABASE: %s" % DATABASE)


def lambda_handler(event, context):
    print("export started")
    log_env_vars()

    conn = get_conn()
    exported_rows = export_event_count(conn)
    conn.close()
    print("exported_rows: %s" % exported_rows)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "exported_rows": exported_rows
        }),
    }
