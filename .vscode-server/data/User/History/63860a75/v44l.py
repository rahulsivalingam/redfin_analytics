from datetime import timedelta, datetime
import pandas as pd
from airflow.operators.python import PythonOperator
import boto3
import os
import glob

s3 = boto3.client('s3')
target_bucket_name = "redfin-transformed-data-yt"
raw_data_bucket = "redfin-raw-data-yt"
prefix = "data/"

def extract_data(**kwargs):
    url = kwargs['url']
    chunk_size = 100000
    small_file_count = 0
    output_list = []
    output_list_s3 = []



    for chunk in pd.read_csv(url, compression='gzip', sep='\t', chunksize = chunk_size):

        #df = pd.read_csv(url, compression='gzip', sep='\t')
        now= datetime.now()
        date_now_string = now.strftime("%d%m%Y%H%M%S")
        file_str = f'redfin_data_chunk_{small_file_count}' #date_now_string
        output_file_path = f"/home/ubuntu/data_files/{file_str}.csv"
        chunk.to_csv(output_file_path, index = False)
        output_list.append(output_file_path)
        small_file_count += 1

        s3_key = f"data/{file_str}.csv"
    
        
        s3.upload_file(output_file_path, raw_data_bucket, s3_key)
        output_list_s3.append(f"s3://{raw_data_bucket}/{s3_key}")
        os.remove(output_file_path)
    
    # Return S3 path instead of local path
    #return f"s3://{s3_bucket}/{s3_key}"
    return output_list_s3


def transform_data(task_instance):
    s3_urls = task_instance.xcom_pull(task_ids="tsk_extract_redfin_data")
    #data= task_instance.xcom_pull(task_ids = "tsk_extract_redfin_data")[0]
    #object_key = task_instance.xcom_pull(task_ids = "tsk_extract_redfin_data")[1]
    data = []
    for s3url in s3_urls:
        df = pd.read_csv(s3url)

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

        data.append(df)

    combined_data = pd.concat(data, ignore_index = True)
    csv_data = combined_data.to_csv(index = False)
    object_key = "processed_redfin_data.csv"
    s3_client.put_object(Bucket= target_bucket_name, Key=object_key, Body=csv_data )