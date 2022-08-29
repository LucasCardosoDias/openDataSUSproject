version = 'v0.0.1' # versao inicial

# Bibliotecas

# - Airfloww
from airflow.models import DAG
from datetime import timedelta, datetime
from airflow.operators.python_operator import PythonOperator

# - Para importação de parametros
import os
# - Tasks
from func.open_data_SUS_lib import open_data_SUS_func as tk

def create_dag(dag_id,
               schedule,
               default_args):

    dag = DAG(dag_id, default_args=default_args, schedule_interval=schedule,
              catchup=False, max_active_runs = 1)

    # ------------------------------------------------------------------------

    # - Task init_etl
    t_init_etl = PythonOperator(
        task_id='init_etl',
        python_callable=tk.init_etl,
        dag=dag
    ) 

    # - Task request_api
    t_request_api = PythonOperator(
        task_id='request_api',
        python_callable=tk.request_data_api,
        dag=dag
    )
    
    # - Task insert_DynamoDB
    t_insert_DynamoDB = PythonOperator(
        task_id='insert_DynamoDB',
        python_callable=tk.insert_DynamoDB,
        dag=dag
    )    

    # - Task insert_RDS_PostgresDB
    t_insert_RDS_PostgresDB = PythonOperator(
        task_id='insert_RDS_PostgresDB',
        python_callable=tk.insert_RDS_PostgresDB,
        dag=dag
    ) 

    # - Task parquet_files
    t_parquet_files = PythonOperator(
        task_id='parquet_files',
        python_callable=tk.parquet_files,
        dag=dag
    ) 
    
    # - Task end_etl
    t_end_etl = PythonOperator(
        task_id='end_etl',
        python_callable=tk.end_etl,
        dag=dag
    ) 
    
    # Tasks arc
    (t_init_etl >> t_request_api >>  
     [t_insert_DynamoDB, t_insert_RDS_PostgresDB, t_parquet_files] 
     >> t_end_etl)
    
    return dag
#-----------------------------------------------------------------------------

# DAG
schedule = "0 23 1-31/4 * *"
dag_id = "open_data_SUS_dag"
args = {
    'owner': 'lucas.cardoso',
    'depends_on_past': False,
    'start_date': datetime(2021, 5, 3),
    'email': 'lucas.cardoso@gmail.com.br',
    'email_on_failure': True,
    'email_on_retry': False,
    'retries':  0,
    'retry_delay': timedelta(minutes=1),
    'concurrency':  1
}
globals()[dag_id] = create_dag(dag_id, schedule, args)
# ----------------------------------------------------------------------------
