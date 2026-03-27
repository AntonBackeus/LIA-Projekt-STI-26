# Data pipeline instructions

The data pipeline has 3 different modules to keep track of:

    The database: Timescaledb
    The dashboard: Grafana
    The ingestion tool: "app.py"
    The orcestrator: Docker

Docker creates the other 3 modules via the docker compose. Make sure docker is running on your computer if you are not running linux. Make sure you are using the version of data_pipeline that is created for your operating system. Currently linux has a slightly different setup with needs to be used compared to windows/mac.

Docker also runs the ingestion tool with custom image using the Dockerfile. To run the project just run "docker compose up" when in the data_pipeline folder in a terminal, -d can be added to remove logs in the terminal. To close it run "docker compose down", -v can be added if containers crash repeatedly or you want to clear persistent memory. It is recommended to run "docker compose build" if you use "docker compose down -v" as it will make sure your fixes are applied.

The Dockerfile and requirements.txt in /etl should not be changed unless you are familiar with docker and the ingestion tool as they are needed to make it work properly.

The .env file is used to make sure all variables are synced between files. If you create a variable meant to be used between more than one file make sure you add it there and reference it in your code instead of adding multiple hard coded instances as it will make changes harder to implement.

## Timescaledb

Timescale is a time series extension of the postgres database. When created by the docker compose it will use the init.sql file in the db folder to generate tables for the database. Make sure when editing it you use "IF NOT EXISTS" as it will run the code each time the container is spun up and risks unintended behavior if a table with the same name exists and you do not use it. Also mark all time series tables as a hypertable as that is how timescale differentiates from normal and time series tables.

## Grafana

Grafana is a live focused dashboards that are focused on showing data in real time. When created by docker it will use the provisioning folder in the grafana folder to set up the datasource (timescale) and locate any saved dashboards. It is therefore important to make sure the grafana volumes in the compose match provisioning and that the dashboards intended to be used are saved as json objects in the dashboard-json folder. Grafana can store multiple dashboards in the folder som feel free to add any tests into the code for later refinement.

## Data ingestion

The data ingestion is a python code tool created for this specific pipeline. It will have a sorting algorithm to sort through data from an omron robot and store it to timescale. Since it is currently looking hard or even impossible to make the init.sql and data ingestion tool configured by a config file it will have to be hardcoded to match each table to a separate ingestion function. This shouldnt be a problem for the current project but for anyone modifying the pipeline or taking part of it be aware if you change one you need to change both.

## Env

The .env file is responsible for configuring most of the containers, while an example version is pushed to github to help future users have and easier time setting up the project is is highly recommended to change some values for security reasons and not published anywhere except where it is used. The env has some comments to help decide what to change.

## Future robot connector?

The data ingestion currently do not have a tool to connect to the robot. It is recommended to try and combine the IOT robot connector with app.py to potentially have it running whenever the data ingestion tool is active since it otherwise will have nowhere to send the data to. Cooperation between IOT and DE teams could be usefull for this.