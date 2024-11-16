import sys, os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipelines.sheets_to_pg import (
    download_google_sheet,
    transform_clickup_data,
    ingest_to_postgres,
)


# Variables
SHEET_ID = Variable.get("CLICKUP_SHEET_ID")
SHEET_NAME = Variable.get("CLICKUP_SHEET_NAME")
TABLE_NAME = Variable.get("CLICKUP_DWH_TABLE_NAME")
HOST = Variable.get("POSTGRES_HOST")
PORT = Variable.get("POSTGRES_PORT")
USER = Variable.get("POSTGRES_USER")
PASSWORD = Variable.get("POSTGRES_PASSWORD")
DATABASE = Variable.get("POSTGRES_DB")

# connection URL for public Google Sheet as CSV
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# Define the DAG
with DAG(
    "CLICKUP_DATA_TO_PG",
    start_date=datetime(2024, 11, 15),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    download_sheet_task = PythonOperator(
        task_id="download_clickup_sheet",
        python_callable=lambda: download_google_sheet(CSV_URL),
    )

    transform_task = PythonOperator(
        task_id="transform_clickup_data",
        python_callable=lambda ti: transform_clickup_data(
            ti.xcom_pull(task_ids="download_clickup_sheet")
        ),
    )

    ingest_to_postgres_task = PythonOperator(
        task_id="ingest_clickup_data_to_postgres",
        python_callable=lambda ti: ingest_to_postgres(
            ti.xcom_pull(task_ids="transform_clickup_data"),
            USER,
            PASSWORD,
            HOST,
            PORT,
            DATABASE,
            TABLE_NAME,
        ),
    )

    # task order order
    download_sheet_task >> transform_task >> ingest_to_postgres_task
