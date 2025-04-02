from airflow import DAG
from datetime import datetime, timedelta

default_args = {
    'owner': 'Rahul',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 20),
    'email': ['dengineer420@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': datetime(second=15)
}

with DAG('redfin_analytics_dag',
    default_args=default_args,
    catchup=False
    #schedule_interval= '@weekely'

) as DAG