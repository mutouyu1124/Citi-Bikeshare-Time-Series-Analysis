# Citi-Bike-Time-Series-Analysis

This repo is for building a time-series analysis to make forecasts for the number of bikes at Times Squre station. Collecting data, training algorithms and make forecasts will all be here.

## Collecting data

In this process, `config.yml` provides all the information needed for grabbing data:
* API_URL: the url of Citi Bike API (https://feeds.citibikenyc.com/stations/stations.json )
* DB_NAME: the name of database
* USER: the user name of database
* PWD: the password of database
* TABLE: name of the table that used to store data
* DB_TYPE: the type of database (PostgreSQL)

An example of config.yml can be found at  [`config.yml_example`](https://pages.github.com/)

### [bikeinfo.py](https://pages.github.com/)

Use this script to grab the status of every Citi Bike station through Citi Bike API, 

Run like
```
python bikeinfo.py config.yml
```

In order to grab the data every 2 minutes, I launched an AWS t2.micro EC2 instance and installed PostgreSQL database on the instance. Upload `bikeinfo.py` and  `config.yml` and run a cron job, the collected data are stored at the PostgreSQL database.

Run like
```
*/2 * * * * python bikeinfo.py config.yml
```
