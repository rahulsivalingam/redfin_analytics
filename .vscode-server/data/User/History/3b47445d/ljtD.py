from airflow import DAG
from datetime import datetime, timedelta

url_by_city = 'https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/city_market_tracker.tsv000.gz'

default_args = {
    'owner': 'Rahul',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 20),
    'email': ['dengineer420@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(second=15)
}

with DAG('redfin_analytics_dag',
    default_args=default_args,
    catchup=False
    #schedule_interval= '@weekly'
    ) as dag:

    extract_redfin_data = PythonOperator(
        task_id = 'tsk_extract_redfin_data',
        python_callable = extract_data,
        op_kwargs = {'url': url_by_city}
    )