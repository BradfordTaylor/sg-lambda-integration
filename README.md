# SageMaker Lambda Integration Demonstration

This GitHub project demonstrates methods for integrating SageMaker models with a larger system.

The context of the project is to "count" events that occur in the system within 5 minute intervals,
call SageMaker to get prediction (or expectation) for how many events should happen based on the model, store the results
and send an alert if the actual count of events is outside a defined threshold.
This project also provides lambdas to demonstrate how the model might be automatically retrained using Lambdas and events.

## Requirements
This project is implemented in AWS SageMaker and Lambdas.
To fully execute it, you must have an AWS Account.
Running these Lambdas and SageMaker notebook code will result in charges on your AWS Account.

Some Lambdas can be tested locally using Docker and AWS Serverless Application Model (SAM).
To execute these Lambdas locally you need:

* [`Python 3`](https://www.python.org/download/releases/3.0/)
* [`Docker`](https://www.docker.com/get-started)
* [`AWS CLI`](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
* [`SAM CLI`](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) (Serverless Application Model)

## Quickstart
 1. Update the `docker-compose.yml` file by adding values for `MYSQL_ROOT_PASSWORD` and `MYSQL_PASSWORD`.
 1. In the root directory of the project execute: `docker network create sg_lambda_integration_default`
 1. In the root directory, excute: `docker-compose up` to run MySQL from a Docker container.
 1. In your browser, enter the url `http://localhost:8080`
 1. Log into SQL Adminer with the root user/password used in the `docker-compose.yml` file
 1. Run the full SQL script found in `sql/create_db.sql` in SQL Adminer to create the DB schema
 1. See the `README.md` file in the directory of the Lambda you want to test
 
Requirements for each individual Lambda can be found in the README.md file of the Lambda's directory.

## Use Case Overview
The web application has specific events that are initated by users of the site.
The number of events that occur follow general trends.
At times there is an abnormal number of these events that occur.
We want to use a machine learning model developed in SageMaker to determine if the number of events that occur within a five minute window is within an expected norm.

## Architecture

The architecture of this demonstration uses the following technologies:
* SageMaker is used to create the model.
* Lambdas are executed once a minute to
  * Copy events from the general system (in our demonstration, we will be simulating these events with `listener_sim`)
  * Aggregate the count of events within a give minute window (`collect`)
  * Calling the SageMaker endpoint to get a prediction and determine if the count is within an expected threshold (`predict`)
  * Create an alert if it is outside of the threshold (`predict`)
  * Storing the results (`predict`)
* Lambdas are executed once a week to
  * Export the previous years worth of data to a csv file (`export`)
  * Retrain the model exposed by the endpoint with the new data (`train`)
  * Update the endpoint with the new model (`deploy`)
* MySQL is used to store data for the Lambdas and extracted for use in SageMaker modeling and training
* SNS is used to create an alert during anomaly detection
* S3 is used to extract data from MySQL and by SageMaker
* S3 events are used to start lambdas to train and deploy a re-trained model to an endpoint

### Lambdas

The Lambdas in this project can generally be divided into two groups: Lambdas run once a minute to detect anomalies and
Lambdas run once a week to retrain the model.

The Lambdas that detect anomalies are each independently executed once a minute. They work together as described below.

#### Detection Lambdas

##### `listener_sim`
The purpose of this Lambda would be to take data from the main system and copy it to the anomaly detection system.
In this demonstration the Lambda is a simulation that creates data.  
A production implementation would retrieve it's data from a source database, an event bus or some other source.

The data is copied from it's source for long term storage and so that any type of aggregation may be created for the data scientist.

##### `collect`
This Lambda aggregates the raw data in a format useful for data scientist.

In this demonstration, that "format" is a count of events that occur every five minutes.  
This, or another Lambda, could aggregate the data in a different way if required by the model.
For example, it could aggregate the number of events every five minutes per user or for specific users.

The table that `collect` aggregates the data into is exported to S3 for model development.
It is also used to aggregate data in real time so that the `predict` Lambda to use as arguments to the SageMaker endpoint. 

##### `predict`
This lambda:
 1. Retrieves any aggregated rows that do not have predictions
 1. Calls the SageMaker endpoint to get a prediction
 1. Creates an SNS message if the actual aggregation is outside acceptable boundaries from the prediction
 1. Stores the results in the database

#### Re-Training Lambdas

The Lambdas that retrain the model are "chained" together with events, with the first Lambda being scheduled to run once a week.
They work together as described below.

##### `export`
A CloudWatch event schedules the execution of this Lambda once a week.
It extracts the content of the aggregation table from the past year into a S3 file.

##### `train`
The `train` Lambda is triggered by a CreateObject event of the S3 bucket used by the `export` Lambda.
It's purpose is to re-train the model on the new data that has been exported.  
The model created from this training is written to the S3 bucket configured by an environment variable. 

It is written in such a way as to not have to "know" about specific details of how the model was trained.
It accomplishes this by using the SageMaker API to retrieve the previous information of the model's training and using those same parameters for the re-training.
In order to accomplish this, some assumptions have to be made about the naming of the existing model's training.
In this implementation, the assumption is that previous training job name starts with `linear-learner`.

There is some inherent risk in this approach.  
An alternative would be to code the Lambda to have the same parameters that were used during training.
This information could be retrieved from environment variables or a database.
The draw-back would be that extra work is required from the data scientist or developer to ensure that the parameters match what was in the notebook.

##### `deploy`
This Lambda is executed as a result of a CreateObject event of the S3 bucket used by the `train` Lambda.
It's purpose is to deploy the updated model to the existing endpoint. 
The deployment API used keeps the existing endpoint available with the same name as it is being updated.
This provides for a zero downtime update.  

Similar to the `train` Lambda, it assumes a naming convention of the model and endpoint to retrieve existing information to use for configuration.   

### SageMaker
A description of the SageMaker architecture, how to create models and endpoints is outside the scope of this demonstration.
There is a lot of information generally available describing how use SageMaker.
This project assumes that you have an endpoint created by SageMaker that exposes a single model (not a model pipeline).

To create a sample endpoint for use with this demonstration, see the README.md in the `notebook/` directory.






