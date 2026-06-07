import logging
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "etl"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "analytics"))

from data.generate_data import main as generate_data
from etl.upload_to_s3 import main as upload_to_s3
from etl.extract_from_s3 import extract
from etl.transform import transform
from etl.load_to_redshift import load
from analytics.queries import run_all_queries

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_step(step_name, func, *args):
    logger.info(f"STEP START: {step_name}")
    start = time.time()
    result = func(*args)
    elapsed = round(time.time() - start, 2)
    logger.info(f"STEP DONE: {step_name} completed in {elapsed}s")
    return result


def main():
    pipeline_start = time.time()
    logger.info("Pipeline starting")

    run_step("Generate Data", generate_data)
    run_step("Upload to S3", upload_to_s3)
    df_raw = run_step("Extract from S3", extract)
    df_clean = run_step("Transform", transform, df_raw)
    run_step("Load to Redshift", load, df_clean)
    run_step("Analytics", run_all_queries)

    total = round(time.time() - pipeline_start, 2)
    logger.info(f"Pipeline complete. Total time: {total}s")


if __name__ == "__main__":
    main()