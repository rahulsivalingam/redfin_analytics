from datetime import timedelta, datetime
import pandas as pd
from airflow.operators.python import PythonOperator
import boto3

s3_client = boto3.client('s3')
target_bucket_name = "redfin-transformed-data-yt"

def extract_data(**kwargs):
    url = kwargs['url']
    chunk_size = 100000
    small_file_count = 0
    output_list = []
    for chunk in pd.read_csv(url, compression='gzip', sep='\t', chunk_size = chunk_size):

        #df = pd.read_csv(url, compression='gzip', sep='\t')
        now= datetime.now()
        date_now_string = now.strftime("%d%m%Y%H%M%S")
        file_str = f'redfin_data_chunk_{small_file_count}_{date_now_string}' #date_now_string
        output_file_path = f"/home/ubuntu/{file_str}.csv"
        chunk.to_csv(output_file_path, index = False)
        output_list.append(output_file_path)
        small_file_count += 1
    return output_list


def transform_data(task_instance):
    data= task_instance.xcom_pull(task_ids = "tsk_extract_redfin_data")[0]
    object_key = task_instance.xcom_pull(task_ids = "tsk_extract_redfin_data")[1]
    df = pd.read_csv(data)

    df['city'] = df['city'].replace(',','')
    cols = ['period_begin','period_end','period_duration', 'region_type', 'region_type_id', 'table_id',
    'is_seasonally_adjusted', 'city', 'state', 'state_code', 'property_type', 'property_type_id',
    'median_sale_price', 'median_list_price', 'median_ppsf', 'median_list_ppsf', 'homes_sold',
    'inventory', 'months_of_supply', 'median_dom', 'avg_sale_to_list', 'sold_above_list', 'parent_metro_region_metro_code', 'last_updated']
    df = df[cols]
    df = df.dropna()


    df['period_begin'] = pd.to_datetime(df['period_begin'])
    df['period_end'] = pd.to_datetime(df['period_end'])

    df["period_begin_in_years"] = df['period_begin'].dt.year
    df["period_end_in_years"] = df['period_end'].dt.year


    df["period_begin_in_months"] = df['period_begin'].dt.month
    df["period_end_in_months"] = df['period_end'].dt.month

    month_dict = {
    "period_begin_in_months": {
        1:'Jan',
        2:'Feb',
        3:'Mar',
        4:'Apr',
        5:'May',
        6:'Jun',
        7:'Jul',
        8:'Aug',
        9:'Sep',
        10:'Oct',
        11:'Nov',
        12:'Dec'
    },
    "period_end_in_months": {
                1:'Jan',
        2:'Feb',
        3:'Mar',
        4:'Apr',
        5:'May',
        6:'Jun',
        7:'Jul',
        8:'Aug',
        9:'Sep',
        10:'Oct',
        11:'Nov',
        12:'Dec'
        
    }
    }

    df = df.replace(month_dict)

    print("Number of rows: ", len(df))
    print("Number of columns: ", len(df.columns))

    csv_data = df.to_csv(index = False)
    object_key = f"{object_key}.csv"
    s3_client.put_object(Bucket= target_bucket_name, Key=object_key, Body=csv_data )