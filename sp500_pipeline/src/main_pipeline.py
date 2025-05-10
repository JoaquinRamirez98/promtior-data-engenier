import logging

from . import config
from .data_extraction import get_sp500_companies_data
from .data_transformation import transform_data
from .database_operations import create_connection, save_data_to_db

# Configure root logger for the entire application.
# This ensures all loggers created via logging.getLogger(__name__) inherit this config.
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT, force=True)
logger = logging.getLogger(__name__) # Get logger for this specific module

def run_pipeline():
    """
    Executes the full S&P 500 data pipeline:
    1. Extracts data from Wikipedia.
    2. Transforms the raw data into a clean, structured format.
    3. Loads the transformed data into a local SQLite database.
    """
    logger.info("========== Starting S&P 500 Data Pipeline ==========")

    # --- 1. Extraction Phase ---
    logger.info(">>> Step 1: Extracting data from Wikipedia...")
    raw_df = get_sp500_companies_data()
    
    if raw_df is None:
        logger.error("Extraction process failed or returned no DataFrame. Pipeline aborted.")
        return
    if raw_df.empty:
        logger.warning("Extraction returned an empty DataFrame. Pipeline aborted as no data to process.")
        return
    logger.info(f"Extraction successful. {len(raw_df)} raw records fetched.")

    # --- 2. Transformation Phase ---
    logger.info(">>> Step 2: Transforming data...")
    transformed_df = transform_data(raw_df)

    if transformed_df is None: # transform_data now returns None on empty input or major failure
        logger.error("Transformation process failed or resulted in no data. Pipeline aborted.")
        return
    if transformed_df.empty: # Should be caught by 'is None' but as a safeguard
        logger.warning("Transformation returned an empty DataFrame. Pipeline aborted.")
        return
    logger.info(f"Transformation successful. {len(transformed_df)} records processed.")

    # --- 3. Load Phase ---
    logger.info(">>> Step 3: Loading data to SQLite database...")
    conn = create_connection(config.DB_PATH)
    if conn:
        try:
            save_data_to_db(transformed_df, conn, config.DB_TABLE_NAME)
            logger.info(f"Data successfully loaded. Database is at: {config.DB_PATH}")
        finally: # Ensure connection is closed even if save_data_to_db fails
            conn.close()
            logger.debug("Database connection closed.")
    else:
        logger.error("Failed to establish database connection. Data not loaded.")

    logger.info("========== S&P 500 Data Pipeline Finished Successfully ==========")

if __name__ == "__main__":
    # This allows the pipeline to be run directly using: python -m src.main_pipeline
    run_pipeline()