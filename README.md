# Citi-Bikeshare-Time-Series-Analysis

This repo is for building a time-series analysis to make forecasts for the number of bikes at Times Squre station. Collecting data, training algorithms and make forecasts will all be here.

## Collecting data

In this process, `config.yml` provides all the information needed for grabbing data:
* API_URL: the url of Citi Bike API (https://feeds.citibikenyc.com/stations/stations.json )
* DB_NAME: the name of database
* USER: the user name of database
* PWD: the password of database
* TABLE: name of the table that used to store data
* DB_TYPE: the type of database (PostgreSQL)

### [bikeinfo.py](https://pages.github.com/)

Use this script to grab the status of every Citi Bike station through Citi Bike API, 

Run like
```
python bikeinfo.py config.yml
```

