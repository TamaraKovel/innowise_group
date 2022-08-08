import os
import pandas as pd
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pymongo

dag = DAG('tiktok', description='tiktok_DAG',
          schedule_interval='* 5 * * *',
          start_date=datetime(2017, 3, 20), catchup=False)

    
def extract_dataset():
    data = pd.read_csv("/home/tkovel/airflow/dags/tiktok_google_play_reviews.csv")
    data.to_csv('/home/tkovel/airflow/dags/tiktok.csv')

def transform_dataset():
    data = pd.read_csv('/home/tkovel/airflow/dags/tiktok.csv')
    data.dropna(inplace = True)
    data.replace("null", "-", regex=True)
    data.sort_values(by='at', ascending=False)
    data['content'] = data['content'].replace(to_replace=r'[^A-Za-z0-9\.!()-;:\'\"\,?@ ]+', value=r'', regex=True)
    data.to_csv('/home/tkovel/airflow/dags/update_tiktok.csv')

def load_dataset():
    upd_data = pd.read_csv('/home/tkovel/airflow/dags/update_tiktok.csv')
    d_data = upd_data.to_dict(orient="records")
    client = pymongo.MongoClient("localhost", 27017)
    db = client["tiktok_test"]
    db.pushing_file.insert_many(d_data)

extract_data = PythonOperator(
    task_id='extract_dataset', 
    python_callable=extract_dataset, 
    dag=dag
    )

transform_data = PythonOperator(
    task_id='transform_dataset', 
    python_callable=transform_dataset, 
    dag=dag
    )

load_data = PythonOperator(
    task_id='load_dataset', 
    python_callable=load_dataset, 
    dag=dag
    )

extract_data >> transform_data >> load_data
