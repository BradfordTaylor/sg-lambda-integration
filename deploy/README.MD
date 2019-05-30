# Deploy Lambda

This Lambda is responsible for deploying the model that results from the retraining started by the `train` Lambda.


## Overview

Since the `train` Lambda starts the training but returns before the training is complete,
this Lambda is executed from a CloudWatch S3 event that is sent whenever a new object is created in the S3 bucket.  
The Lambda validates the key (directory and filename) in the event before proceeding.

Like the `train` Lambda, it uses naming convention and SageMaker APIs to retrieve the existing endpoint configuration and update it.
It uses the `updateEndpoint` SageMaker API to complete the update.
This API allows the updating of an existing SageMaker endpoint with zero downtime.
The name of the endpoint will stay the same after the update is complete.


## Local Testing
The steps below can be used to test this Lambda locally.  
Local testing *does* require an AWS account and will make changes to it.
It will change the AWS SageMaker endpoint to use a new model. 

 1. Ensure that have the tools in the root directory `README.md` Requirements section installed and working 
 1. Complete the steps listed in the  root directory `README.md` Quickstart section
 1. Update the environment variables in the `template.yml` file (see Environment Variables section below) 
 1. Use the command `sam build --use-container && sam local invoke` to test


### Environment Variables

* `MODEL_PREFIX` - The value of this variable is used to confirm the S3 key of the created file, find the model configuration and create the new model used for the endpoint.
* `ENDPOINT_PREFIX` - The value of this variable is used to find the endpoint configuration and create the new endpoint configuration used to update the endpoint. 

_NOTE: Although the `MODEL_PREFIX` and `ENDPOINT_PREFIX` are defined to have the same values in this project, it is possible that their values will be different.
For this reason, two environment variables have been defined._

 
