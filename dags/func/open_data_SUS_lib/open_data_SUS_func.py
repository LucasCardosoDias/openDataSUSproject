# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 15:39:54 2022

@author: lucas.cardoso
"""

# - Bibliotecas 
import os
import json
import boto3
import requests
import pandas as pd

# - Bibliotecas Próprias
from func.sqlconnInOut import sqlconnInOutObj
from func.open_data_SUS_lib import repository as rp

#%% - Pré-processamento
def processing_info(df):
    
    '''
    Parameters
    ----------
    df : dataframe
        Dataframe contendo informações da requisicao de dados via API OpenSUS.

    Returns
    -------
    df_filter: dataframe
        Dataframe apos processamento.

    '''        
    list_columns = rp.repository_items('list_columns')
    
    df_filter = df[list_columns]
    
    replace_dict = rp.repository_items('replace_dict')
    
    
    df_filter = df[list_columns].rename(columns = replace_dict) \
                .astype(str).replace('None', 'Info. Desconhecida')
    
    return df_filter

#%% - Requisicoes da API OpenDataSUS
def request_data_api():
    
    '''
    Description
    -------
        Realiza a requisicao de dados do openDataSUS via API.
        Aplica-se o processamento nos dados requisitados.
        Persiste os dados em uma tabela no banco de dados DAG_DB_DATABASE
    '''    
    
    url = "https://imunizacao-es.saude.gov.br/_search"
    
    payload = json.dumps({
      "size": 100
    })
    headers = {
      'Authorization': 'Basic aW11bml6YWNhb19wdWJsaWM6cWx0bzV0JjdyX0ArI1Rsc3RpZ2k=',
      'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    r = response.json()['hits']['hits']
    
    # Dados brutos para o datalake
    df = pd.json_normalize(r)
    
    # Dados processados
    df_filter = processing_info(df)

    DAG_sqlconn.insertValuesInTable(df_filter, 'df_filter', if_exists = "replace")

#%% - AWS DynamoDB
def clientDynamoDB(TableName):
    
    '''
    Parameters
    ----------
    TableName : String
        Nome da tabela que os dados serao persistidos no AWS DynamoDB

    Returns
    -------
    table : object
        Objeto para comunicacao entre a task e a plataforma AWS
    '''    
    
    ACCESS_KEY = os.environ["ACCESS_KEY"]
    SECRET_KEY = os.environ["SECRET_KEY"]
    
    session = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    )
    
    client = session.client('dynamodb', region_name="us-east-1")
    DB = session.resource('dynamodb', region_name="us-east-1")
    table = DB.Table(TableName)
    
    return table

def dynamo_get_item(table, Primary_Column_Name, Primary_Key):

    '''
    Description
    ----------
        Funcao para requisitar dados no AWS DynamoDB

    Parameters
    ----------
    table : object
        Objeto para comunicacao entre a task e a plataforma AWS
    Primary_Column_Name: String
        Nome da chave primaria da tabela
    Primary_Key: String
        Valor da chave primaria
    
    
    Returns
    -------
    itemsDynamoDB : json
        Arquivo json com informacoes dos dados na tabela requisitada
    '''      


    itemsDynamoDB = table.get_item(Key={Primary_Column_Name:Primary_Key})
    return itemsDynamoDB
    
def request_DynamoDB():
    
    '''
    Description
    ----------
        Task que realiza a requisicao de dados no AWS DynamoDB
    '''    
    
    TableName = 'dynamo_project'    
    table = clientDynamoDB(TableName)

    Primary_Column_Name = 'paciente_id'
    Primary_Key = 'a3b8ff95f44d2555b5152a8d9f792d616ecd4ba8397c937c02d5c486efc72590'
        
    itemsDynamoDB = dynamo_get_item(table, Primary_Column_Name, Primary_Key)

    print(itemsDynamoDB["Item"])
    
def insert_DynamoDB():
    
    '''
    Description
    ----------
        Task utilizada para persistir os dados no AWS DynamoDB
    '''  
    
    colunas_select = rp.repository_items('colunas')
    
    query_select = 'Select * from df_filter'

    df_filter = DAG_sqlconn.selectFromTable(inputQuery = query_select, 
                                             columnsSelect = colunas_select)
    
    TableName = 'dynamo_project'    
    table = clientDynamoDB(TableName)
    
    for i, row in df_filter.iterrows():
        insertValues = table.put_item(Item = row.to_dict())     


#%% - AWS RDS - PostgresSQL
def insert_RDS_PostgresDB():

    '''
    Description
    ----------
        Task utilizada para persistir os dados no AWS RDS PostgresSQL
    '''  
    
    colunas_select = rp.repository_items('colunas')
    
    query_select = 'Select * from df_filter'

    df_filter = DAG_sqlconn.selectFromTable(inputQuery=query_select, 
                                             columnsSelect=colunas_select)

    dtype = rp.repository_items('dtype')
    
    RDS_sqlconn.insertValuesInTable(df_filter, 'opendata_covid19', 
                                    if_exists = "replace", dtype = dtype)

#%% - Parquet files

def parquet_files():

    '''
    Description
    ----------
        Task utilizada para persistir os dados em formato parquet.
    '''  
    
    colunas_select = rp.repository_items('colunas')
    
    query_select = 'Select * from df_filter'

    df_filter = DAG_sqlconn.selectFromTable(inputQuery=query_select, 
                                             columnsSelect=colunas_select)
    df_filter.to_parquet('/opt/airflow/dags/parquet_files/opendata_covid19.parquet')

#%% Init e end tasks
def init_etl():
    
    '''
    Description
    ----------
        Task inicial que informa a versao da DAG.
    ''' 
    
    version = '0.0.1'
    print('vesion: ', version)
    
    
def end_etl():
    
    '''
    Description
    ----------
        Task final que realiza a limpeza das tabelas criadas pelas tasks
        no DAG_DB_DATABASE.
    ''' 
    
    query_delete = 'DROP TABLE IF EXISTS  df_filter'
    DAG_sqlconn.executeDirectQuery(query_delete)
#-----------------------------------------------------------------------------

# - Parametros para comunicao com o DAG_DB_DATABASE
parameters_DAG_DB = {
    "user": os.environ["DAG_DB_USER"],
    "password": os.environ["DAG_DB_PASSWORD"],
    "host": os.environ["DAG_DB_HOST"],
    "port": os.environ["DAG_DB_PORT"],
    "database": os.environ["DAG_DB_DATABASE"]
}
# SQL Conn Class
DAG_sqlconn = sqlconnInOutObj(parameters_DAG_DB)

# - Parametros para comunicao com o AWS RDS PostgresSQL 
parameters_RDS = {
    "user": os.environ["RDS_USER"],
    "password": os.environ["RDS_PASSWORD"],
    "host": os.environ["RDS_HOST"],
    "port": os.environ["RDS_PORT"],
    "database": os.environ["RDS_DATABASE"]
}
# SQL Conn Class
RDS_sqlconn = sqlconnInOutObj(parameters_RDS)
#----------------------------------------------------------------------------    

    
    
    
    
    
    
    
    
    
    
    
    
    
    