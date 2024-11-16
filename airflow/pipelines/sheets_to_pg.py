import logging
import pandas as pd
from sqlalchemy import create_engine

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


def download_google_sheet(csv_url: str):
    try:
        df = pd.read_csv(csv_url)
        logging.info("Google Sheet data downloaded.")
        return df.to_dict()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise


def ingest_to_postgres(
    transformed_data,
    user: str,
    password: str,
    host: str,
    port: str,
    database: str,
    table_name: str,
):
    try:
        df_transformed = pd.DataFrame(transformed_data)

        engine = create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        )
        df_transformed.to_sql(table_name, con=engine, if_exists="append", index=False)
        logging.info(
            "Transformed data successfully ingested into PostgreSQL using pandas"
        )
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise


def transform_float_data(sheet_data):
    try:
        df = pd.DataFrame(sheet_data)

        # transform data
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        df["estimated_hours"] = df["estimated_hours"].fillna(0)
        for date_column in ["start_date", "end_date"]:
            df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
            df[date_column] = df[date_column].dt.strftime("%Y-%m-%dT%H:%M:%S")
            
        df = df[df["end_date"] >= df["start_date"]]
        df["estimated_hours"] = (
            pd.to_numeric(df["estimated_hours"], errors="coerce").fillna(0).astype(int)
        )
        df = df.drop_duplicates()
        string_columns = ["client", "project", "role", "name", "task"]
        for col in string_columns:
            df[col] = df[col].str.strip().str.title()

        logging.info("Transformed DataFrame:")
        logging.info(df.head())

        logging.info("Transformed DataFrame:")
        logging.info(df.head())
        return df.to_dict()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise


def transform_clickup_data(sheet_data):
    try:
        df = pd.DataFrame(sheet_data)

        # transform data
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        string_columns = ["client", "project", "name", "task", "note"]
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].str.strip().str.title()
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df["date"] = df["date"].dt.strftime("%Y-%m-%dT%H:%M:%S")
        if "hours" in df.columns:
            df["hours"] = pd.to_numeric(df["hours"], errors="coerce")
        if "billable" in df.columns:
            df["billable"] = (
                df["billable"].str.strip().str.lower().map({"yes": True, "no": False})
            )
        critical_columns = ["client", "project", "name", "task", "date", "hours"]
        df = df.dropna(subset=critical_columns)
        if "note" in df.columns:
            df["note"] = df["note"].fillna("No Note")
        df = df.drop_duplicates()

        logging.info("Transformed DataFrame:")
        logging.info(df.head())
        return df.to_dict()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise
