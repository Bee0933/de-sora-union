from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd
import logging

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

# Google Sheet ID and sheet name
SHEET_ID = Variable.get("CLICKUP_SHEET_ID")
SHEET_NAME = Variable.get("CLICKUP_SHEET_NAME")
TABLE_NAME = Variable.get("CLICKUP_DWH_TABLE_NAME")

# connection URL for public Google Sheet as CSV
CSV_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'


def download_google_sheet(**kwargs):
    try:
        df = pd.read_csv(CSV_URL)
        kwargs['ti'].xcom_push(key='sheet_data', value=df.to_dict())
        logging.info("Google Sheet data downloaded and pushed to XCom")
    except Exception as e:
        logging.error(f'An error occured: {e}')

def transform_data(**kwargs):
    try:
        ti = kwargs['ti']
        sheet_data = ti.xcom_pull(key='sheet_data', task_ids='download_google_sheet')
        df = pd.DataFrame(sheet_data)
        
        # transform data
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        string_columns = ['client', 'project', 'name', 'task', 'note']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].str.strip().str.title()
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        if 'hours' in df.columns:
            df['hours'] = pd.to_numeric(df['hours'], errors='coerce')
        if 'billable' in df.columns:
            df['billable'] = df['billable'].str.strip().str.lower().map({'yes': True, 'no': False})
        critical_columns = ['client', 'project', 'name', 'task', 'date', 'hours']
        df = df.dropna(subset=critical_columns)
        if 'note' in df.columns:
            df['note'] = df['note'].fillna('No Note')
        df = df.drop_duplicates()

        logging.info("Transformed DataFrame:")
        logging.info(df.head())
        kwargs['ti'].xcom_push(key='transformed_data', value=df.to_dict())
    except Exception as e:
        logging.error(f'An error occured: {e}')

def ingest_to_postgres(**kwargs):
    try:
        ti = kwargs['ti']
        transformed_data = ti.xcom_pull(key='transformed_data', task_ids='transform_data')
        df_transformed = pd.DataFrame(transformed_data)

        host = Variable.get("POSTGRES_HOST")
        port = Variable.get("POSTGRES_PORT")
        user = Variable.get("POSTGRES_USER")
        password = Variable.get("POSTGRES_PASSWORD")
        database = Variable.get("POSTGRES_DB")

        engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}')
        df_transformed.to_sql(TABLE_NAME, con=engine, if_exists='append', index=False)
        logging.info("Transformed data successfully ingested into PostgreSQL using pandas")
    except Exception as e:
        logging.error(f'An error occured: {e}')


# Define the DAG
with DAG(
    'CLICKUP_DATA_TO_PG',
    start_date=datetime(2024, 11, 15),
    schedule_interval='@daily',
    catchup=False,
) as dag:

    download_sheet_task = PythonOperator(
        task_id='download_google_sheet',
        python_callable=download_google_sheet,
        provide_context=True
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        provide_context=True  
    )

    ingest_to_postgres_task = PythonOperator(
        task_id='ingest_to_postgres',
        python_callable=ingest_to_postgres,
        provide_context=True  
    )

    # task order order
    download_sheet_task >> transform_task >> ingest_to_postgres_task
