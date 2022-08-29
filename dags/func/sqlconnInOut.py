import csv
import pandas as pd
from io import StringIO
from sqlalchemy.sql import text
from sqlalchemy import create_engine

class sqlconnInOutObj:
    def __init__(self, parameters):
        self.parameters = parameters
        self.parameters['port'] = self.parameters['port'] if self.parameters['port'] else "5432"
        self.parameters['connection_string'] = (
            'postgresql://'
            f'{self.parameters["user"]}'
            ':'
            f'{self.parameters["password"]}'
            '@'
            f'{self.parameters["host"]}'
            ':'
            f'{self.parameters["port"]}'
            '/'
            f'{self.parameters["database"]}'
        )
        
    def startSQLeng(self):
        engine = create_engine(self.parameters['connection_string'])
        return engine

    def insertCOPYMethod(self, table, conn, keys, data_iter):
        dbapi_conn = conn.connection
        with dbapi_conn.cursor() as cur:
            s_buf = StringIO()
            writer = csv.writer(s_buf)
            writer.writerows(data_iter)
            s_buf.seek(0)

            columns = ', '.join('"{}"'.format(k) for k in keys)
            if table.schema:
                table_name = '{}.{}'.format(table.schema, table.name)
            else:
                table_name = table.name

            sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
                table_name, columns)
            cur.copy_expert(sql=sql, file=s_buf)

    def insertValuesInTable(self, df, tableName, if_exists, dtype=None):
        engine = self.startSQLeng()
        if dtype:
            df.to_sql(tableName, engine, index=False, if_exists = if_exists, method= self.insertCOPYMethod, dtype = dtype)
        else:
            df.to_sql(tableName, engine, index=False, if_exists = if_exists, method= self.insertCOPYMethod)
        print('Insertion finished')


    def selectFromTable(self, inputQuery, columnsSelect=None, dtype=None):
                
        try:
            engine = self.startSQLeng()
            print(f'Executing the query: {inputQuery}')
            
            sql = text(inputQuery)
                
            if dtype:
                df = pd.read_sql_query(sql=sql, con=engine, dtype=dtype, coerce_float=False)
            else:
                df = pd.read_sql_query(sql=sql, con=engine, coerce_float=False)
                            
            if columnsSelect is not None:
                df.columns = columnsSelect
                            
            return df
        except Exception as e:
            print(f'Error: {inputQuery}')
            raise e

    def executeDirectQuery(self, DirectQuery):

        try:
            engine = self.startSQLeng()
            with engine.connect() as con:
                print(f'Executing the query: {DirectQuery}')
                rs = con.execute(DirectQuery)
                
        except Exception as e:
            print(f'Error: {DirectQuery}')
            raise(e)
