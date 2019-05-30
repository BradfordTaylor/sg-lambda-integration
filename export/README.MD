# Export Lambda

This Lambda is responsible for exported the previous year's aggregated data into a file that resides in a S3 bucket.
This file is used as a data source for automated retraining of the model by other Lambas.
The csv file can also be used in SageMaker Jupyter notebooks for the purpose of developing models.
 

## Overview
The Lambda is scheduled to be executed once a week.  

The Lambda uses a single SQL `SELECT INTO OUTFILE S3` statement to export the the data.

## Local Testing
The steps below can be used to test this Lambda locally.  
Local testing *does* require an AWS account and will make changes to it.
A S3 bucket is required where the exported data will be stored.

 1. Ensure that have the tools in the root directory `README.md` Requirements section installed and working 
 1. Complete the steps listed in the  root directory `README.md` Quickstart section
 1. Update the environment variables in the `template.yml` file (see Environment Variables section below) 
 1. Use the command `sam build --use-container && sam local invoke` to test


### Environment Variables

* `DATABASE` - The database or schema name where the data resides
* `DB_USER`  - The database user to use for database authentication
* `PASSWORD` - The password associated with the `DB_USER` to use for database authentication
* `PORT`     - The port used to connect to the database
* `HOST`    - The hostname of the database
* `S3_BUCKET`    - The name of the S3 bucket to store the exported data

_NOTE: The value of_ `docker.for.mac.host.internal` _is used so that the Docker image SAM uses to execute the Lambda can connect to the MySQL Docker image created by the_ `docker-compose.yml` _file in the root directory.
This value will need to be updated for other OSes._

 
