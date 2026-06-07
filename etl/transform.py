import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Starting transformation")
    initial_rows = len(df)

    df = df.drop_duplicates(subset=["transaction_id"]).copy()
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        logger.warning(f"Removed {duplicates_removed} duplicate transaction IDs")

    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["amount"] = df["total_amount"].round(2)
    df["unit_price"] = df["unit_price"].round(2)
    df["quantity"] = df["quantity"].astype(int)
    df["customer_phone"] = df["customer_phone"].astype(str)

    df["mpesa_ref"] = df["mpesa_ref"].fillna("N/A")

    df["year"] = df["transaction_date"].dt.year
    df["month"] = df["transaction_date"].dt.month
    df["month_name"] = df["transaction_date"].dt.strftime("%B")
    df["hour_of_day"] = df["transaction_date"].dt.hour
    df["day_of_week"] = df["transaction_date"].dt.strftime("%A")
    df["is_weekend"] = df["transaction_date"].dt.dayofweek >= 5

    df["revenue_band"] = pd.cut(
        df["amount"],
        bins=[0, 1000, 10000, 50000, float("inf")],
        labels=["Low", "Medium", "High", "Premium"],
    )

    df["is_mpesa"] = df["payment_method"] == "M-Pesa"

    columns_to_keep = [
        "transaction_id",
        "transaction_date",
        "year",
        "month",
        "month_name",
        "hour_of_day",
        "day_of_week",
        "is_weekend",
        "shop_name",
        "county",
        "product_category",
        "quantity",
        "unit_price",
        "amount",
        "payment_method",
        "mpesa_ref",
        "is_mpesa",
        "revenue_band",
        "customer_phone",
    ]

    df = df[columns_to_keep]

    null_counts = df.isnull().sum()
    null_columns = null_counts[null_counts > 0]
    if not null_columns.empty:
        logger.warning(f"Null values remaining: {null_columns.to_dict()}")

    logger.info(f"Transformation complete. Rows before: {initial_rows}, rows after: {len(df)}")
    return df


if __name__ == "__main__":
    from extract_from_s3 import extract
    df_raw = extract()
    df_clean = transform(df_raw)
    print(df_clean.dtypes)
    print(df_clean.head())