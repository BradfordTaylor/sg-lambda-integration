from __future__ import print_function
import os
import json
import boto3
from datetime import datetime


SM_CLIENT = boto3.client("sagemaker")
MODEL_PREFIX = os.environ["MODEL_PREFIX"]
ENDPOINT_PREFIX = os.environ["ENDPOINT_PREFIX"]


def get_model_name(prefix):
    print("getting model job name with prefix %s" % prefix)
    results = SM_CLIENT.list_models(NameContains=prefix,
                                    SortBy="CreationTime",
                                    SortOrder="Descending")
    return results["Models"][0]["ModelName"]


def get_model_config(model_name):
    print("getting model config for %s" % model_name)
    return SM_CLIENT.describe_model(ModelName=model_name)


def create_model(prefix, model_url, config):
    print("creating model")
    model_name = "%s-%s" % (prefix, datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    return SM_CLIENT.create_model(ModelName=model_name,
                                  ExecutionRoleArn=config["ExecutionRoleArn"],
                                  Containers=[
                                      {
                                          "Image": config["Containers"][0]["Image"],
                                          "Environment": config["Containers"][0]["Environment"],
                                          "ModelDataUrl": model_url
                                      }
                                  ])


def get_endpoint_config(prefix):
    print("getting endpoint config for %s" % prefix)
    e_configs = SM_CLIENT.list_endpoint_configs(NameContains=prefix,
                                                SortBy="CreationTime",
                                                SortOrder="Descending",
                                                MaxResults=1)
    return SM_CLIENT.describe_endpoint_config(EndpointConfigName=e_configs["EndpointConfigs"][0])


def create_endpoint_config(prev_config, model_config, endpoint_prefix):
    print("creating new endpoint config")
    ec_name = "%s-config-%s" % (endpoint_prefix, datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    SM_CLIENT.create_endpoint_config(EndpointConfigName=ec_name,
                                     ProductionVariants=[
                                         {
                                             "InitialInstanceCount": prev_config["ProductionVariants"][0]["InitialInstanceCount"],
                                             "InstanceType": prev_config["ProductionVariants"][0]["InstanceType"],
                                             "ModelName": model_config["ModelName"],
                                             "VariantName": prev_config["ProductionVariants"][0]["VariantName"],
                                             "InitialVariantWeight": prev_config["ProductionVariants"][0]["InitialVariantWeight"]
                                         }
                                     ])
    return ec_name


def get_endpoint(prefix):
    print("getting endpoint with prefix %s" % prefix)
    results = SM_CLIENT.list_endpoints(NameContains=prefix,
                                       SortBy="CreationTime",
                                       SortOrder="Descending",
                                       MaxResults=1)
    return results["Endpoints"][0]


def update_endpoint(endpoint, config_name):
    print("updating endpoint")
    return SM_CLIENT.update_endpoint(EndpointConfigName=config_name,
                                     Endpoint=endpoint["EndpointName"])


def lambda_handler(event, context):
    print("deploy started")

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    if not key.startswith(MODEL_PREFIX):
        return {
            "statusCode": 400,
            "body": "Not processing new file %s in bucket %s" % (key, bucket)
        }

    model_url = "s3://%s/%s" % (bucket, key)
    name = get_model_name(MODEL_PREFIX)
    model_config = get_model_config(name)
    create_model(MODEL_PREFIX, model_url, model_config)
    endpoint_config = get_endpoint_config(ENDPOINT_PREFIX)
    new_endpoint_config_name = create_endpoint_config(endpoint_config, model_config, ENDPOINT_PREFIX)
    endpoint = get_endpoint(ENDPOINT_PREFIX)
    endpoint_arn = update_endpoint(endpoint, new_endpoint_config_name)
    print("endpoint_arn: %s" % endpoint_arn)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "endpoint_arn": endpoint_arn
        }),
    }
