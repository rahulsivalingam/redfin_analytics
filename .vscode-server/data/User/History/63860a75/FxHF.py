from datetime import deltatime, datetime
import pandas as pd
from airflow.operators.python import PythonOperator

def extract_data(**kwargs):
    url = kwargs['url']
    df = pd.read_csv(url, compression='gzip', sep='\t')
    now= datetime.now()
    date_now_string = now.strftime("%d%m%Y%H%M%S")
    file_str = 'redfin_data_' + date_now_string
    df.to_csv(f"{file_str}.csv", index = False)
    output_file_path = f"/home/ubunto/{file_str}.csv"
    output_list = [output_file_path, file_str]
    return output_list
