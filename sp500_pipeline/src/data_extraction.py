# src/data_extraction.py
import requests
from bs4 import BeautifulSoup, Tag
import pandas as pd
import logging
from typing import List, Dict, Optional

from . import config 

logger = logging.getLogger(__name__)
# BasicConfig for logger is usually set in the main entry point (main_pipeline.py)

def fetch_html(url: str, timeout: int = 15) -> Optional[str]:
    """
    Fetches HTML content from the given URL.

    Args:
        url: The URL to fetch.
        timeout: Request timeout in seconds.

    Returns:
        HTML content as a string if successful, None otherwise.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)
        logger.info(f"Successfully fetched HTML from {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return None

def parse_sp500_table(html_content: str) -> Optional[pd.DataFrame]:
    """
    Parses the S&P 500 companies table from the provided HTML content.
    It first tries to locate the table by its specific ID 'constituents'.
    If not found, it falls back to searching for tables with class 'wikitable sortable'
    and identifies the correct one by looking for a unique header (e.g., "GICS Sector").
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    table: Optional[Tag] = None

    # Attempt 1: Direct selection by ID (most specific and preferred)
    logger.debug("Attempting to find table directly by id='constituents'")
    table = soup.find('table', id='constituents')

    if table:
        logger.info("Successfully found table by id='constituents'.")
        if 'wikitable' in table.get('class', []) and 'sortable' in table.get('class', []):
            logger.debug("Confirmed table also has 'wikitable sortable' classes.")
        else:
            # This might indicate a page structure change, but we proceed if ID matched.
            logger.warning("Table found by ID lacks expected 'wikitable sortable' classes.")
    else:
        # Attempt 2: Fallback - search by class and identify by unique header content.
        logger.warning("Could not find table by id='constituents'. Falling back to class and header search.")
        all_wikitables = soup.find_all('table', {'class': 'wikitable sortable'})
        
        if not all_wikitables:
            logger.error("Fallback failed: No tables with class 'wikitable sortable' found.")
            return None

        logger.debug(f"Found {len(all_wikitables)} tables with class 'wikitable sortable'. Inspecting headers...")
        target_header_text = "GICS Sector" # Assumed unique identifier for the correct table
        found_correct_table_in_fallback = False
        for i, t_candidate in enumerate(all_wikitables):
            headers_th = t_candidate.find_all('th')
            header_texts_in_current_table = [th.text.strip() for th in headers_th]
            logger.debug(f"  Fallback Candidate {i} - Headers: {header_texts_in_current_table}")
            if target_header_text in header_texts_in_current_table:
                table = t_candidate
                logger.info(f"Identified correct table via fallback (Candidate {i}) by header '{target_header_text}'.")
                found_correct_table_in_fallback = True
                break
        
        if not found_correct_table_in_fallback:
            logger.error(f"Fallback failed: Could not identify table by header '{target_header_text}'.")
            return None

    # --- Header Parsing and Column Mapping ---
    rows_data: List[Dict[str, str]] = []
    headers_html_elements = table.find_all('th') 
    
    # Extract actual header texts from the selected table for mapping
    actual_header_texts_from_html = [th.text.strip() for th in headers_html_elements]
    logger.debug(f"Actual HTML Headers from Selected Table: {actual_header_texts_from_html}")

    html_header_to_index_map: Dict[str, int] = {
        text: i for i, text in enumerate(actual_header_texts_from_html)
    }
    
    column_map_for_df: Dict[str, int] = {} # Stores {df_col_name: html_table_index}
    successfully_mapped_count = 0
    for df_col_name, html_header_text_from_config in config.TABLE_COLUMN_MAPPING_KEYS.items():
        if html_header_text_from_config in html_header_to_index_map:
            column_map_for_df[df_col_name] = html_header_to_index_map[html_header_text_from_config]
            successfully_mapped_count += 1
        else:
            logger.warning(f"Configuration Mismatch: HTML header '{html_header_text_from_config}' (for DF column '{df_col_name}') not found in selected table. Actual headers: {list(html_header_to_index_map.keys())}")

    # Ensure a minimum number of columns are mapped to proceed
    # This prevents parsing with largely incorrect or missing column definitions
    if successfully_mapped_count == 0:
         logger.error(f"Critical: Mapped 0 columns. Aborting parse. Headers in table: {list(html_header_to_index_map.keys())}")
         return None
    elif successfully_mapped_count < len(config.TABLE_COLUMN_MAPPING_KEYS):
        logger.warning(f"Partial Map: Mapped {successfully_mapped_count}/{len(config.TABLE_COLUMN_MAPPING_KEYS)} columns. Proceeding, but review config/HTML if critical data is missing.")
    else:
         logger.info(f"Successfully mapped all {successfully_mapped_count} columns: {column_map_for_df}")

    # --- Row Parsing ---
    tbody = table.find('tbody')
    if not tbody:
        logger.error("No <tbody> found in the selected table. Cannot parse rows.")
        return None
        
    table_rows = tbody.find_all('tr') 

    for i, row_tr in enumerate(table_rows):
        cells_td = row_tr.find_all('td')
        
        max_needed_index = max(column_map_for_df.values()) if column_map_for_df else -1
        
        if len(cells_td) <= max_needed_index:
            row_content_debug = [c.text.strip() for c in cells_td]
            if any(row_content_debug): # Log only if the skipped row had some content
                 logger.debug(f"Skipping row {i+1} (insufficient cells: {len(cells_td)}, need >{max_needed_index}): {row_content_debug}")
            continue

        company_data_row: Dict[str, str] = {}
        for df_col_name, html_col_idx in column_map_for_df.items():
            try:
                company_data_row[df_col_name] = cells_td[html_col_idx].text.strip()
            except IndexError:
                # This should be rare if max_needed_index check is correct
                logger.error(f"IndexError for col '{df_col_name}' (idx {html_col_idx}) in row {i+1}. Should have been caught by cell count check.")
                company_data_row[df_col_name] = "" # Default to empty string on unexpected error
        
        rows_data.append(company_data_row)

    if not rows_data:
        logger.warning("No data rows were extracted from the table's tbody.")
        return None

    df = pd.DataFrame(rows_data)
    logger.info(f"Successfully parsed {len(df)} company rows into DataFrame.")
    return df


def get_sp500_companies_data() -> Optional[pd.DataFrame]:
    """Orchestrates the fetching and parsing of S&P 500 company data."""
    if not logging.getLogger().hasHandlers(): # Ensure logger is configured if module run standalone
         logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
         
    logger.info("--- Starting S&P 500 Data Extraction Process ---")
    html_content = fetch_html(config.WIKIPEDIA_URL)
    if not html_content:
        logger.error("Aborting extraction: Failed to fetch HTML content.")
        return None
    
    companies_df = parse_sp500_table(html_content)
    if companies_df is None: # Covers cases where parsing fails or yields no data
        logger.error("Aborting extraction: Parsing the S&P 500 table failed or returned no DataFrame.")
        return None
    
    logger.info("--- S&P 500 Data Extraction Process Finished Successfully ---")
    return companies_df

# Removed the __main__ block for direct testing from here,
# as it's better practice to test via a separate test script or main_pipeline.