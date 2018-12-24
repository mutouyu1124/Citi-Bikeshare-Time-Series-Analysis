import numpy as np
import pandas as pd

import argparse
import requests
import json

from sqlalchemy import create_engine
import psycopg2
import logging
import time
import os
import sys
import yaml

LOG_FILENAME = os.path.join(os.path.curdir,'bike.log')
logging.basicConfig(filename = LOG_FILENAME, level = logging.INFO)

# def parse_args():
# 	ap = argparse.ArgumentParser()
# 	ap.add_argument("-d","--db_name",type = str,required = True, help = "the database name")
# 	ap.add_argument("-u","--user",type = str, required = True, help = "the user name")
# 	ap.add_argument("-p","--pwd",type = str, required = True, help = "password")
# 	ap.add_argument("-t","--table",type = str, required = True, help = "table name")
# 	ap.add_argument("-dt","--db_type",type = str,required = True, help = "type of database")
# 	ap.add_argument("-a","--api_url",type = str,required = True, help = "api url")
# 	ap.add_argument("--create", action='store_true',help='Whether or not to create a database table first.')
# 	args = ap.parse_args()
# 	return args

def load_config(conf_file):
    """Load database configuration file as global variables"""

    config = yaml.load(open(conf_file, 'r'))
    global DB_NAME
    DB_NAME = config['DB_NAME']
    global USER
    USER = config['USER']
    global PWD
    PWD = config['PWD']
    global TABLE
    TABLE = config['TABLE']
    global DB_TYPE
    DB_TYPE = config['DB_TYPE']
    global API_URL
    API_URL = config['API_URL']

def get_info(api_url):
	# get station information and covert to DataFrame
	stations = requests.get(api_url)
    status_code = stations.status_code
    stations = json.loads(stations.text)
    stationlist = stations['stationBeanList']
    stationdf = pd.DataFrame(stationlist)
	stationdf = stationdf.loc[stationdf['stationName'] == 'E 16 St & 5 Ave'].reset_index(drop=True)

	values = np.array([stations['executionTime']])
    values = np.repeat(values, stationdf.shape[0])
    ex = pd.DataFrame(index=np.arange(stationdf.shape[0]),columns=['executionTime'])
    ex['executionTime'] = values

    cols = stationdf.columns.tolist() # Store for a hot minute
    stationdf = pd.concat([ex, stationdf], axis=1, ignore_index=True)
    stationdf.columns = ['executionTime'] + cols
	return stationdf, status_code


def write_info(api_url, engine, table):
	post_cols = ['executionTime',
				 'availableBikes',
				 'availableDocks',
				 'id',
				 'lastCommunicationTime',
				 'latitude',
				 'longitude',
				 'stAddress1',
				 'stationName',
				 'statusKey',
				 'statusValue',
				 'testStation',
				 'totalDocks']

	logging.info('{}: write_info()'.format(time.ctime()))

	try:
		df,status = get_info(api_url)
		if status != 200:
			logging.error('Error: bad request at: {}'.format(time.ctime()))
		else:
			df[post_cols].to_sql(table,engine,if_exists = 'append',index = False)
	except:
		logging.error('Error: bad request at: {}'.format(time.ctime()))


def create_table(db, user, pwd, table):
	conn = psycopg2.connect(dbname=db, user = user, password = pwd, host='*')
	query = """
			CREATE TABLE {table}(
			executionTime TIMESTAMP,
			availableBikes SMALLINT,
			availableDocks SMALLINT,
			id SMALLINT,
			lastCommunicationTime' TIMESTAMP,
			latitude NUMERIC(8,6),
			longitude NUMERIC(8,6),
			stAddress1 VARCHAR(100),
			stationName VARCHAR(100),
			statusKey SMALLINT,
			statusValue VARCHAR(100),
			testStation BOOLEAN,
			totalDocks SMALLINT
			)
			""".format(**{'table':table})
	cur = conn.cursor()
	cur.execute(query)
	conn.commit()
	cur.close()
	conn.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Citibike listener')
    parser.add_argument('config', help='config file with DB and API params')
    parser.add_argument('--create', action='store_true',
                        help='Whether or not to create a database table first.')
    args = parser.parse_args()

    load_config(args.config)
    if args.create:
        create_table(DB_NAME, USER, PWD, TABLE)

    engine_str = '{}://{}:{}@localhost/{}'.format(DB_TYPE, USER, PWD, DB_NAME)
    engine = create_engine(engine_str)

    write_info(API_URL, engine, TABLE)