Redfin data Pipeline 

 

This project aims to extract data from the redfin website, process it and push the processed cleaned data to a s3 bucket, further which it will be loaded into snowflake to have an enhanced connector to load data into powerBI for data analysis by building a dashboard.  

 

This project uses a vs code editor connected to an ec23 instance. The dag is created using airflow and 2 step process is followed. The first step of the dag is to load the data from Redfin, which was done by using a redfin API to connect to the redfin website for data. This was a 3 GB file and hence took a lot of memory and computation. The first work around to this issue was to use a larger ec2 instance but this did not resolve this issue and increasing the cost due to the larger ec2 instance. Hence a batch processing approach was taken to break down the downloaded data to numerous batches of 100k records each and as and when one data batch was downloaded, it was uploaded to a s3 bucket and deleted from the ec3 memory to support a faster computation.    

Once all the batches of the raw data was loaded in to the s3 bucket, the second stage of processing was started which takes each batch of data, processes the data (deleting certain columns, getting rid of null values, deleting unwanted rows and so on) and finally each chunk of this processed data was held in a list to which other processed chunks of data were appended before finally converting to a csv and uploading to another s3 bucked designed to hold processed data.  

The next stage was to load this data into snowflake to have a better connector to powerBI. Snowflake requires creating a new database, a schema inside which we create a table to support the data coming in from the s3.  we will also have to create a file format specifying the type of file, the delimiter and other such parameters. We then create another schema that describes the connection details to the s3 using various keys  and the specifying the file format that we just created in the previous step.  now a snow pipe schema is created along with a copy command that loads data from the s3 file to the local table we created earlier. The pipeline is created to ensure that this data load can be automated, for instance, once the processed data file is in the desired s3 bucket, this event will trigger the snow pipe to load data to the snowflake table which will be further user for the powerBI data visualization.  

 

 

 

 

Ec2 starting commands:  

 

Sudo apt update 

Sudo apt install pip3-python 

 

sudo apt install python3.12-venv 

python3 -m venv redfin_venv    (creating the virtual environment) 

source redfin_venv/bin/activate. (activating the virtual environment) 

 

 

Pip install pandas 

Pip install boto3 

pip install --upgrade awscli 

pip install apache-airflow 

 

Create access key  (taken from account, will not be downloadable again) 

Access key:             

Secret access key:      

 

Aws configure  

 

Airflow standalone 

username:   password:     (generated by the console upon running command) 

 

Enable inbound rule on port 8080 from the security group  

 

Open vs code and connect to the ec2 instance  

Open the airflow folder and create folder dags and create a pythn file to start dag coding  

 

In snowflake you need to create a new schema for everything to make things kept out fine and separately.  

Need to create a format type in snowflake to specify the kind of data coming in. 

 

Create a table to support the data . Create an intermediate stage as a staging layer to support the data coming in from s3.  

 
