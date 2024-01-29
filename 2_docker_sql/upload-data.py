
import pandas as pd
import psycopg2
import argparse
from sqlalchemy import create_engine
from time import time
import os


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    csv_name = 'output.csv'

    # download csv
    os.system(f"wget {url} -O {csv_name}.gz")
    os.system(f"gzip -d {csv_name}.gz")

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=10000)

    df = next(df_iter)
    df['lpep_dropoff_datetime'] = pd.to_datetime(df['lpep_dropoff_datetime'])
    df['lpep_pickup_datetime'] = pd.to_datetime(df['lpep_pickup_datetime'])

    df.head(n=0).to_sql(name=f'{table_name}', con=engine, if_exists='replace')
    total=0
    while True:
        t_start = time()

        df = next(df_iter)
        total+=len(df)
        df['lpep_dropoff_datetime'] = pd.to_datetime(df['lpep_dropoff_datetime'])
        df['lpep_pickup_datetime'] = pd.to_datetime(df['lpep_pickup_datetime'])
        df.to_sql(name=f'{table_name}', con=engine, if_exists='append', index=False)

        t_end = time()
        print(f'inserted {total}')
        print('inserted another chunk..., took %.3f seconds' % (t_end - t_start))


if __name__== '__main__':

    parser = argparse.ArgumentParser(
                        prog='upload-data',
                        description='Ingest ny taxi data to Postgresql')

    # user pass wqord host port db name talbe name
    # url of the csv

    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument('--table-name', help='tablename for postgres')
    parser.add_argument('--url', help='url where to ingest data from')

    args = parser.parse_args()

    main(args)