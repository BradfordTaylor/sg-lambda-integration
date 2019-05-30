# Listener Simulation Lambda

This Lambda is responsible for simulating new events being created and copied into the application.
The `get_new_rows` function can be changed to simulate a different creation of events.
In a test or production environment, this Lambda would be replaced by one that would copy events from the source system. 

## Overview
The Lambda is executed once a minute by a CloudWatch event.

The `get_new_rows` function in `listener_sim` first looks at the `Events` table to find the latest datetime of our data.
In the case of this implementation, it then random simulates a count of events based on the current hour.  
Generally, during the day and early evening a higher count will occur than at other times.
At night, no counts will be generated. 

For a production environment it should be implemented such that it will attempt to retrieve all new events since the last time it was run.
It it could do this by retrieving all rows from a table who's ID is greater than the last ID in the `Event` table.
Another method would be to retrieve all of the events from a queue that has been filled since the last time the Lambda executed.

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

 
