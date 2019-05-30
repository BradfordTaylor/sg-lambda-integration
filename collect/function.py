from __future__ import print_function
import sys
import os
import json
import pymysql

DATABASE = os.environ['DATABASE']
USER = os.environ['DB_USER']
PASSWD = os.environ['PASSWORD']
PORT = os.environ['PORT']
HOST = os.environ['HOST']
QUERY_INSERT_COLLECT = " insert into EventCount(dt_bucket, actual_count)" \
                       "  SELECT\n" \
                       "     from_unixtime(ceiling((UNIX_TIMESTAMP(occurrence_timestamp) / 300 )) * 300)\n" \
                       "                            as dt_bucket,\n" \
                       "         COUNT(occurrence_timestamp) as actual_count\n" \
                       "      FROM Event\n" \
                       " where occurrence_timestamp > ifNull(" \
                       "                                    (select dt_bucket " \
                       "                                       from EventCount " \
                       "                                      order by dt_bucket desc limit 1), " \
                       "                                    DATE_SUB(NOW(),INTERVAL 1 YEAR))\n" \
                       " GROUP BY dt_bucket;\n"


def get_conn():
    try:
        print('Connect to DB: %s' % HOST)
        return pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE,  connect_timeout=5)
    except:
        print('Database Connection Failed: exception %s' % sys.exc_info()[1])
        return 'Failed'


def insert_collect(conn):
    print("Inserting collected count of events")
    cursor = conn.cursor()
    cursor.execute(QUERY_INSERT_COLLECT)
    conn.commit()
    rowcount = cursor.rowcount
    cursor.close()
    return rowcount


def log_env_vars():
    print("HOST: %s" % HOST)
    print("USER: %s" % USER)
    print("DATABASE: %s" % DATABASE)


def lambda_handler(event, context):
    print("Collected started")
    log_env_vars()

    conn = get_conn()
    collected_rows = insert_collect(conn)
    conn.close()
    print("row_count: %s" % collected_rows)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "row_count": collected_rows,
            # "location": ip.text.replace("\n", "")
        }),
    }
