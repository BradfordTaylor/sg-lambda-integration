from __future__ import print_function
import os
import json
import boto3
from datetime import datetime


SM_CLIENT = boto3.client("sagemaker")
TRAINING_JOB_PREFIX = os.environ["TRAINING_JOB_PREFIX"]


def get_training_name(prefix):
    print("getting training job name with prefix %s" % prefix)
    results = SM_CLIENT.list_training_jobs(NameContains=prefix,
                                           StatusEquals='Completed',
                                           SortBy="CreationTime",
                                           SortOrder="Descending")
    return results["TrainingJobSummaries"][0]["TrainingJobName"]


def get_training_config(training_name):
    print("getting training config for %s" % training_name)
    return SM_CLIENT.describe_training_job(TrainingJobName=training_name)


def update_training_config(bucket, key, config):
    print("updating training config")
    new_s3_uri = "s3://%s/%s" % (bucket, key)
    config["InputDataConfig"][0]["DataSource"]["s3DataSource"]["S3Uri"] = new_s3_uri
    return config


def start_training(prefix, config):
    print("start training")

    training_job_name = "%s-%s" % (prefix, datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    config["AlgorithmSpecification"]["MetricDefinitions"] = None
    return SM_CLIENT.create_training_job(AlgorithmSpecification=config["AlgorithmSpecification"],
                                         OutputDataConfig=config["OutputDataConfig"],
                                         ResourceConfig=config["ResourceConfig"],
                                         RoleArn=config["RoleArn"],
                                         StoppingCondition=config["StoppingCondition"],
                                         TrainingJobName=training_job_name,
                                         HyperParameters=config["HyperParameters"],
                                         InputDataConfig=config["InputDataConfig"],
                                         Tags=config["Tags"])


def lambda_handler(event, context):
    print("training model")

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    if not key.startswith("export"):
        return {
            "statusCode": 400,
            "body": "Not processing new file %s in bucket %s" % (key, bucket)
        }

    training_name = get_training_name(TRAINING_JOB_PREFIX)
    training_config = get_training_config(training_name)
    new_config = update_training_config(bucket, key, training_config)
    training_arn = start_training(TRAINING_JOB_PREFIX, new_config)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "training_arn": training_arn
        }),
    }
