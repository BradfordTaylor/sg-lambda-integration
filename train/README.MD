# Train Lambda

This Lambda is responsible for retraining the SageMaker model with new data made available in a S3 bucket.

This function also serves as an example of using SageMaker training APIs to retrain a model.
The API call that initiates the training is asynchronous in that is starts the training process but returns before the training is complete.  

## Overview
This Lambda is executed from a CloudWatch S3 event that is sent whenever a new object is created in the S3 bucket. 
The Lambda validates the key (directory and filename) in the event before proceeding.

This Lambda uses AWS SDK to make SageMaker API calls to retrain the model with the data in the S3 bucket that results from the `export` Lambda.
It reads the configuration of the existing model to configure the training that it conducts.
The result is that it does not have to be aware or configured with training configuration parameters that was used to create the model.
It accomplishes this through a standard naming convention of the model and conducting SageMaker API calls to retrieve the last training job and use it's parameters to retrain.
The resulting trained model is then saved to the same S3 bucket as that the export file was written to.

Although using the previously trained model parameters to re-train removes necessity of having the configuration in two components in two different systems (Lambda and SageMaker), this can create issues should "something bad" happen.
If the naming convention is not followed, then the Lambda will either not successfully find a model to use for parameters or will use incorrect model parameters.
Also, if a model is deployed with bad parameters, it will be re-trained with the same bad parameters.

## Local Testing
The steps below can be used to test this Lambda locally.
Local testing *does* require an AWS account and will make changes to it.

It requires the training job information used for the model used in the SageMaker endpoint.
The Lambda will create and start a new training job in AWS SageMaker. 

 1. Ensure that have the tools in the root directory `README.md` Requirements section installed and working 
 1. Complete the steps listed in the  root directory `README.md` Quickstart section
 1. Update the environment variables in the `template.yml` file (see Environment Variables section below) 
 1. Use the command `sam build --use-container && sam local invoke` to test


### Environment Variables

* `EVENT_ANOMALY_MODEL_PREFIX` - This is a prefix used to find the latest specific training job that was used to create the model

 
