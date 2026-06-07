import os
import logging
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

REDSHIFT_HOST = os.getenv("REDSHIFT_HOST")
REDSHIFT_PORT = int(os.getenv("REDSHIFT_PORT"))
REDSHIFT_DB = os.getenv("REDSHIFT_DB")
REDSHIFT_USER = os.getenv("REDSHIFT_USER")
REDSHIFT_PASSWORD = os.getenv("REDSHIFT_PASSWORD")


def get_connection():
    return psycopg2.connect(
        host=REDSHIFT_HOST,
        port=REDSHIFT_PORT,
        dbname=REDSHIFT_DB,
        user=REDSHIFT_USER,
        password=REDSHIFT_PASSWORD,
    )


def create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            transaction_id      VARCHAR(50) PRIMARY KEY,
            transaction_date    TIMESTAMP,
            year                INTEGER,
            month               INTEGER,
            month_name          VARCHAR(20),
            hour_of_day         INTEGER,
            day_of_week         VARCHAR(20),
            is_weekend          BOOLEAN,
            shop_name           VARCHAR(100),
            county              VARCHAR(100),
            product_category    VARCHAR(100),
            quantity            INTEGER,
            unit_price          NUMERIC(12, 2),
            amount              NUMERIC(12, 2),
            payment_method      VARCHAR(50),
            mpesa_ref           VARCHAR(50),
            is_mpesa            BOOLEAN,
            revenue_band        VARCHAR(20),
            customer_phone      VARCHAR(20)
        )
    """)
    logger.info("sales table ready")


def load(df: pd.DataFrame):
    logger.info("Starting load to Redshift")

    df["revenue_band"] = df["revenue_band"].astype(str)
    df["is_weekend"] = df["is_weekend"].astype(bool)
    df["is_mpesa"] = df["is_mpesa"].astype(bool)

    records = list(df.itertuples(index=False, name=None))

    insert_sql = """
        INSERT INTO sales (
            transaction_id, transaction_date, year, month, month_name,
            hour_of_day, day_of_week, is_weekend, shop_name, county,
            product_category, quantity, unit_price, amount, payment_method,
            mpesa_ref, is_mpesa, revenue_band, customer_phone
        ) VALUES %s
        ON CONFLICT (transaction_id) DO NOTHING
    """

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                create_table(cursor)
                psycopg2.extras.execute_values(cursor, insert_sql, records, page_size=100)
                logger.info(f"Inserted {len(records)} records into sales table")
    except Exception as e:
        logger.error(f"Load failed: {e}")
        raise
    finally:
        conn.close()
        logger.info("Database connection closed")

    logger.info("Load complete")


if __name__ == "__main__":
    from extract_from_s3 import extract
    from transform import transform
    df_raw = extract()
    df_clean = transform(df_raw)
    load(df_clean)