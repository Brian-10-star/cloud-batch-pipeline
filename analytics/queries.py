import os
import logging
import psycopg2
import psycopg2.extras
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


def run_query(cursor, title, sql):
    logger.info(f"Running: {title}")
    cursor.execute(sql)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    print(f"\n{'=' * 55}")
    print(f"  {title}")
    print(f"{'=' * 55}")

    col_widths = [max(len(str(col)), max((len(str(row[i])) for row in rows), default=0)) for i, col in enumerate(columns)]
    header = "  " + "  ".join(str(col).ljust(col_widths[i]) for i, col in enumerate(columns))
    print(header)
    print("  " + "-" * (sum(col_widths) + 2 * len(col_widths)))

    for row in rows:
        line = "  " + "  ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row))
        print(line)


def run_all_queries():
    logger.info("Starting analytics queries")
    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            run_query(cursor, "Total Revenue and Transactions by Month", """
                SELECT
                    month_name,
                    COUNT(*) AS total_transactions,
                    ROUND(SUM(amount)::NUMERIC, 2) AS total_revenue
                FROM sales
                GROUP BY month_name, month
                ORDER BY month
            """)

            run_query(cursor, "Top 5 Counties by Revenue", """
                SELECT
                    county,
                    COUNT(*) AS transactions,
                    ROUND(SUM(amount)::NUMERIC, 2) AS total_revenue
                FROM sales
                GROUP BY county
                ORDER BY total_revenue DESC
                LIMIT 5
            """)

            run_query(cursor, "Revenue by Product Category", """
                SELECT
                    product_category,
                    COUNT(*) AS transactions,
                    ROUND(SUM(amount)::NUMERIC, 2) AS total_revenue,
                    ROUND(AVG(amount)::NUMERIC, 2) AS avg_transaction
                FROM sales
                GROUP BY product_category
                ORDER BY total_revenue DESC
            """)

            run_query(cursor, "Payment Method Breakdown", """
                SELECT
                    payment_method,
                    COUNT(*) AS transactions,
                    ROUND(SUM(amount)::NUMERIC, 2) AS total_revenue,
                    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()::NUMERIC, 2) AS pct_of_transactions
                FROM sales
                GROUP BY payment_method
                ORDER BY transactions DESC
            """)

            run_query(cursor, "Top 5 Shops by Revenue", """
                SELECT
                    shop_name,
                    COUNT(*) AS transactions,
                    ROUND(SUM(amount)::NUMERIC, 2) AS total_revenue
                FROM sales
                GROUP BY shop_name
                ORDER BY total_revenue DESC
                LIMIT 5
            """)

            run_query(cursor, "Revenue Band Distribution", """
                SELECT
                    revenue_band,
                    COUNT(*) AS transactions,
                    ROUND(SUM(amount)::NUMERIC, 2) AS total_revenue,
                    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()::NUMERIC, 2) AS pct_of_transactions
                FROM sales
                GROUP BY revenue_band
                ORDER BY
                    CASE revenue_band
                        WHEN 'Low' THEN 1
                        WHEN 'Medium' THEN 2
                        WHEN 'High' THEN 3
                        WHEN 'Premium' THEN 4
                    END
            """)

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise
    finally:
        conn.close()
        logger.info("Analytics complete")


if __name__ == "__main__":
    run_all_queries()