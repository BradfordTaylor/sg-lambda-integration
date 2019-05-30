# Collect Lambda

This Lambda is responsible for aggregating the data in the `Event` table into "buckets" or "counts" of events. 
It executes a single SQL statement that aggregates the data while inserting it into the `EventCount` table. 
It currently aggregates the count of events into five minute buckets.

## Overview
The Lambda is executed once a minute by a CloudWatch event. 
It is designed such that it will attempt to aggregate any data in the `Event` table that has not already been aggregated.
It aggregates any data where the `occurrance_timestamp` of the `Event` table is greater than the newest date of the `dt_bucket` in the `EventCount` table.
If no date is found, it will go back one year from the date it is being run as the the earliest date. 
This approach will not fill in gaps of data that may be missing and only retrieves data later than the latest `dt_bucket` row. 
If the number of rows are too large then the Lambda will run longer than it's timeout. 
This can be worked around by temporarily extending the timeout the Lamba, executing the Lambda locally with a long timeout or manually copying the rows outside of of the Lambda.

## Local Testing
The steps below can be used to test this Lambda locally.  Local testing does not require any configuration or use AWS account resources if using a local MySQL database.

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

_NOTE: The value of_ `docker.for.mac.host.internal` _is used so that the Docker image SAM uses to execute the Lambda can connect to the MySQL Docker image created by the_ `docker-compose.yml` _file in the root directory.
This value will need to be updated for other OSes._

 
