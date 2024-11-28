import os
import connection
import sqlparse
import pandas as pd

if __name__ == '__main__':
    # conn data source
    name_source = 'marketplace_prod'
    conf = connection.config(name_source)
    conn, engine = connection.get_conn(conf, name_source)
    cursor = conn.cursor()

    # conn dwh
    name_source = 'dwh'
    conf = connection.config(name_source)
    conn_dwh, engine_dwh = connection.get_conn(conf, name_source)
    cursor_dwh = conn.cursor()

    # get query string
    path_query = os.path.join(os.getcwd(), 'query')
    query = sqlparse.format(
        open(os.path.join(path_query, 'query.sql'), 'r').read(), strip_comments=True
    ).strip()
    dwh_design = sqlparse.format(
        open(os.path.join(path_query, 'dwh_design.sql'), 'r').read(), strip_comments=True
    ).strip()

    try:
        # get data
        print('[INFO] etl services is running..')
        print(engine)
        df = pd.read_sql(query, engine)

        #create schema dwh
        cursor_dwh.execute(dwh_design)
        conn_dwh.commit()

        #ingest data to dwh
        df.to_sql(
            'dim_orders',
            engine_dwh,
            schema='public',
            if_exists='replace',
            index=False
        )
        print('[INFO] etl services success')

    except Exception as e:
        print('[ERROR] etl services failed')
        print(str(e))
