import os 
import pandas as pd 
from sqlalchemy import create_engine
import pymysql
import time 
import json
import boto3
from botocore.exceptions import ClientError


PASSWORD = os.environ.get('DK_DB_PASSWORD', '')


def get_secret():

    secret_name = "dk_database"
    region_name = "us-east-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    js = json.loads(secret)
    return js['host'], js['password'], js['username']


def get_secret_environmental():
    secret = os.environ.get('dk_database', {
        "username": "akgoyal",
        "password": "wouldntyouliketoknow",
        "host": "localhost", 
    })
    secret = json.loads(secret)
    return secret['host'], secret['password'], secret['username']


def run_sql_query_from_file(file, conn, logger=None):
    """
    Read in a .sql file and gets the results in pandas DF 
    Inputs
    ------
        file: the file location (str)
        conn: Database Connection Object

    Outputs
    -------
        Dataframe containing result set 
    """
    with open(file, 'r') as f:
        query = f.read()

    start = time.time()
    df = pd.read_sql_query(query, conn)
    end = time.time()

    if logger:
        n_rows = df.shape[0]
        n_seconds = '{:.1f}'.format(end - start)
        logger.info(f"Queried from file: {file}, retrieved n_rows: {n_rows}, took {n_seconds}s.")

    return df


def create_connection(use_aws=True,
                      host='localhost',
                      user='akgoyal',
                      database='dk_nba',
                      password=PASSWORD):
    """
    Inputs
    ------
        host: string containing host name
        user: string for the user
        database: string for the database name
        password: string 

    Outputs
    -------
        Connection object
    """
    if use_aws:
        try:
            host, password, user = get_secret_environmental()
        except Exception as e:
            host, password, user = get_secret()

    conn = create_engine('mysql+pymysql://' + user + ':' +
                         password + '@' + host + ':3306/' + database,
                         echo=False)
    return conn


def create_cursor(use_aws=True,
                  host='localhost',
                  user='akgoyal',
                  database='dk_nba',
                  password=PASSWORD):
    if use_aws:
        try:
            host, password, user = get_secret_environmental()
        except Exception as e:
            host, password, user = get_secret()

    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        db=database
    )
    return conn