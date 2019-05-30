# Prediction Lambda

This Lambda is responsible for comparing actual results against a prediction and taking action if needed.
It uses the data aggregated in the `EventCount` table as parameters to call the SageMaker endpoint using SageMaker APIs.
The parameters and results are stored in the `EventPredict` table for analysis.


## Overview
The Lambda is executed once a minute by a CloudWatch event. 

It is designed such that it will attempt to create prediction rows for any data in the `EventCount` table that has not already been predicted; to a maximum of 400 rows. 
It makes predictions for any `event_count_id` in the `EventCount` table not found in the `EventPredict` table. 
This approach should fill in gaps in the prediction table. 
Although inserting prediction data for missing rows will not occur on a single Lambda execution, 
the frequency of execution combined with the maximum number of rows allows the data to eventually "catch-up" to real time as long as the Lambda continues to execute.

The `predict` Lambda is the most involved of the runtime Lambdas because it is responsible for:
1. Finding any rows in the `EventCount` table that do not have predictions 
1. Calling the SageMaker endpoint to retrieve a prediction
1. Making the final decision if the actual count for the row is an anomaly
1. Inserting the data from the prediction into the `EventPredict` table
1. Sending a SNS message if the prediction is outside acceptable parameters

It currently inserts the following data into the EventPredict table:
1. The actual count sent to the prediction
2. The prediction returned from SageMaker
3. A calculation of the standard deviation of the actual count from other rows that match it's parameters 
4. The calculated upper bound that is considered an anomaly
5. The calculated lower bound that is considered an anomaly


The calculation for the standard deviation is done by SQL in the SQL query used against the database. 
The test for whether the actual count is an anomaly is in the Lambda logic but the number of standard deviations that define the upper and lower bounds are configured using environment variables.

## Local Testing
The steps below can be used to test this Lambda locally.  Local testing does requires a SageMaker endpoint configured to retrieve a prediction.

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
* `SM_ENDPOINT` - This is the name of the SageMaker endpoint.
* `HIGH_MULTIPLE` - This is the number of standard deviations above the prediction to detect an anomaly
* `LOW_MULTIPLE` -  - This is the number of standard deviations below the prediction to detect an anomaly
* `ALERT_TOPIC` - This is the SNS topic to send a message to if the actual count is outside acceptable parameters

_NOTE: The value of_ `docker.for.mac.host.internal` _is used so that the Docker image SAM uses to execute the Lambda can connect to the MySQL Docker image created by the_ `docker-compose.yml` _file in the root directory.
This value will need to be updated for other OSes._

 
