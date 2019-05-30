from __future__ import print_function
import sys
import os
import json
import pymysql
import boto3

DATABASE = os.environ['DATABASE']
USER = os.environ['DB_USER']
PASSWD = os.environ['PASSWORD']
PORT = os.environ['PORT']
HOST = os.environ['HOST']
SM_ENDPOINT = os.environ['SM_ENDPOINT']
HIGH_MULTIPLE = float(os.environ['HIGH_MULTIPLE'])
LOW_MULTIPLE = float(os.environ['LOW_MULTIPLE'])
ALERT_TOPIC = os.environ['ALERT_TOPIC']
ALERT_MESSAGE = "Event Anomaly Found\n" \
                "  dt_bucket: %s\n" \
                "  Event Count: %s\n" \
                "  Count Prediction: %s\n" \
                "  Standard Deviation: %s\n"
QUERY_NULL_PREDICTS = "select event_count_id, " \
                      "       actual_count, " \
                      "       DATE_FORMAT(dt_bucket, '%Y-%m-%d %T') as dt_bucket, " \
                      "       (SELECT STDDEV(actual_count) as STDDEV " \
                      "          FROM EventCount " \
                      "         WHERE WEEKDAY(dt_bucket) = WEEKDAY(source.dt_bucket) " \
                      "           AND DATE_FORMAT(dt_bucket, '%H:%i:%S')  = DATE_FORMAT(source.dt_bucket, '%H:%i:%S')) as STDDEV " \
                      "  from EventCount as source " \
                      "         where event_count_id not in (select event_count_id from EventPredict) limit 200"
QUERY_INSERT_PREDICTS = "INSERT INTO EventPredict(" \
                        "                         metric_value, " \
                        "                         event_count_id, " \
                        "                         model_type_id, " \
                        "                         metric_type_id, " \
                        "                         metric_dt)\n " \
                        "       values(" \
                        "              IFNULL(%s,0), " \
                        "              %s, " \
                        "              (SELECT model_type_id from ModelType where model_type = %s)," \
                        "              (SELECT metric_type_id from MetricType where metric_type = %s)," \
                        "              NOW())"
SNS = boto3.client('sns')
SM_RUNTIME = boto3.client('runtime.sagemaker')


def get_conn():
    print("getting db connection")
    try:
        print('Connect to DB: %s' % HOST)
        return pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE,  connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except:
        print('Database Connection Failed: exception %s' % sys.exc_info()[1])
        return 'Failed'


def get_null_predicts(conn):
    print("getting counts without predictions")
    cursor = conn.cursor()
    cursor.execute(QUERY_NULL_PREDICTS)
    results = cursor.fetchall()
    cursor.close()
    return results


def get_predicts(null_predicts):
    print("Getting predictions for %s rows" % len(null_predicts))
    for row in null_predicts:
        response = SM_RUNTIME.invoke_endpoint(EndpointName=SM_ENDPOINT,
                                              ContentType='text/csv',
                                              Body=row["actual_count"])
        result = json.loads(response['Body'].read().decode())
        row["prediction"] = int(result['predictions'][0]['predicted_label'])
        row["up_bound"] = row["prediction"] + (row["STDDEV"] * HIGH_MULTIPLE)
        row["low_bound"] = row["prediction"] - (row["STDDEV"] * LOW_MULTIPLE)
        row["anomaly"] = 0 if row["actual_count"] <= row["up_bound"] else 1
    return null_predicts


def update_predicts(predicts, conn):
    print("inserting predictions")
    if len(predicts) < 1:
        return 0

    cursor = conn.cursor()
    update_data = []
    for row in predicts:
        update_data.append((row["prediction"], row["event_count_id"], "LINEAR", "PREDICTION"))
        update_data.append((row["STDDEV"], row["event_count_id"], "LINEAR", "STDDEV"))
        update_data.append((row["anomaly"], row["event_count_id"], "LINEAR", "ANOMALY"))
        update_data.append((row["actual_count"], row["event_count_id"], "LINEAR", "ACTUAL"))
        update_data.append((row["up_bound"], row["event_count_id"], "LINEAR", "UP_BOUND"))
        update_data.append((row["low_bound"], row["event_count_id"], "LINEAR", "LOW_BOUND"))
    cursor.executemany(QUERY_INSERT_PREDICTS, update_data)
    conn.commit()
    row_count = cursor.rowcount
    cursor.close()
    return row_count if row_count > 0 else 0


def send_alerts(predicts):
    print("sending alerts")
    if len(predicts) < 1:
        return 0

    alert_count = 0
    for row in predicts:
        if row["anomaly"] > 0:
            print("ALERT, ALERT, ALERT")
            alert_count += 1
            SNS.publish(
                TopicArn=ALERT_TOPIC,
                Message=ALERT_MESSAGE % (row["dt_bucket"], row["actual_count"], row["prediction"], row["STDDEV"])
            )
    return alert_count


def log_env_vars():
    print("HOST: %s" % HOST)
    print("USER: %s" % USER)
    print("DATABASE: %s" % DATABASE)


def lambda_handler(event, context):
    print("predict started")
    log_env_vars()

    conn = get_conn()
    null_predicts = get_null_predicts(conn)
    predicts = get_predicts(null_predicts)
    predicts_count = update_predicts(predicts, conn)
    alerts_count = send_alerts(predicts)
    conn.close()
    print("predicts_count: %s, alerts_sent: %s" % (predicts_count, alerts_count))
    return {
        "statusCode": 200,
        "body": json.dumps({
            "predicted_rows": len(predicts),
            "inserted_rows": predicts_count,
            "alerts_sent": alerts_count
        }),
    }
