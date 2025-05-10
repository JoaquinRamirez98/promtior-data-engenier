import pandas as pd
import re
import logging
from typing import Optional, Tuple

from . import config

logger = logging.getLogger(__name__)
# BasicConfig for logger is usually set in the main entry point (main_pipeline.py)

def clean_founded_year(founded_str: Optional[str]) -> Optional[int]:
    """
    Extracts the first 4-digit year from a string.
    Handles various formats and potential non-numeric text.
    """
    if pd.isna(founded_str) or not isinstance(founded_str, str):
        return None
    
    # Regex to find the first occurrence of a 4-digit number (assumed to be the year)
    match = re.search(r'\b(\d{4})\b', founded_str)
    if match:
        return int(match.group(1))
    logger.debug(f"Could not parse year from 'Founded' string: '{founded_str}'")
    return None

def split_headquarters(location_str: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Splits a 'City, State' string into separate City and State components.
    Makes a best effort for common S&P 500 US-based location formats.
    """
    if pd.isna(location_str) or not isinstance(location_str, str):
        return None, None
    
    parts = location_str.split(',')
    if len(parts) >= 2:
        city = parts[0].strip()
        # Assumes the state is the part after the first comma.
        # This is a simplification and might need refinement for more complex international addresses.
        state = parts[1].strip()
        return city, state
    elif len(parts) == 1: 
        # If no comma, unable to reliably split; assign to city and leave state None.
        logger.debug(f"Headquarters location '{location_str}' does not contain a comma for splitting.")
        return location_str.strip(), None
    return None, None # Should not be reached if logic above is complete

def transform_data(df: pd.DataFrame) -> Optional[pd.DataFrame]: # Return Optional[pd.DataFrame]
    """
    Cleans, transforms, and structures the raw S&P 500 data.
    Converts data types, extracts specific information, and selects final columns.
    """
    if df.empty:
        logger.warning("Input DataFrame for transformation is empty. No transformation performed.")
        return None # Return None if input is empty, as no meaningful transformation can occur.

    logger.info(f"Starting data transformation for {len(df)} rows.")
    
    transformed_df = df.copy() # Work on a copy to avoid SettingWithCopyWarning

    # 1. Date Added: Clean and convert to datetime.
    if 'Date_Added' in transformed_df.columns:
        # Remove bracketed references (e.g., [10]) often found in Wikipedia dates
        transformed_df['Date_Added'] = transformed_df['Date_Added'].str.replace(r'\[.*?\]', '', regex=True)
        transformed_df['Date_Added'] = pd.to_datetime(transformed_df['Date_Added'], errors='coerce')
        # 'coerce' will turn unparseable dates into NaT (Not a Time)
    else:
        logger.warning("Column 'Date_Added' not found. It will be missing in the transformed data.")
        # transformed_df['Date_Added'] = pd.NaT # No need to add if not selecting later

    # 2. Founded Year: Extract year from 'Founded' string.
    if 'Founded' in transformed_df.columns:
        transformed_df['Founded_Year'] = transformed_df['Founded'].apply(clean_founded_year)
        # apply() will pass NaN for unparseable years if clean_founded_year returns None
    else:
        logger.warning("Column 'Founded' not found. 'Founded_Year' will be missing.")

    # 3. Headquarters Location: Split into City and State.
    if 'Headquarters_Location' in transformed_df.columns:
        # Apply the split_headquarters function and expand the tuple result into two new columns
        hq_split_series = transformed_df['Headquarters_Location'].apply(
            lambda x: pd.Series(split_headquarters(x), index=['Headquarters_City_temp', 'Headquarters_State_temp'])
        )
        transformed_df['Headquarters_City'] = hq_split_series['Headquarters_City_temp']
        transformed_df['Headquarters_State'] = hq_split_series['Headquarters_State_temp']
    else:
        logger.warning("Column 'Headquarters_Location' not found. City/State columns will be missing.")

    # 4. CIK: Clean (remove non-digits) and convert to nullable Integer.
    if 'CIK' in transformed_df.columns:
        # Remove any non-digit characters before attempting numeric conversion
        cleaned_cik = transformed_df['CIK'].astype(str).str.replace(r'\D', '', regex=True)
        # Convert to numeric, coercing errors to <NA>. Use Int64 for nullable integers.
        transformed_df['CIK'] = pd.to_numeric(cleaned_cik, errors='coerce').astype('Int64')
    else:
        logger.warning("Column 'CIK' not found. It will be missing.")
        
    # Ensure all FINAL_COLUMNS are present, adding them with appropriate nulls if missing from source.
    # This guarantees a consistent output schema.
    final_df = pd.DataFrame()
    for col_name in config.FINAL_COLUMNS:
        if col_name in transformed_df.columns:
            final_df[col_name] = transformed_df[col_name]
        else:
            logger.warning(f"Final column '{col_name}' not generated during transformation. Will be added as a column of nulls.")
            # Assign appropriate null type based on expected content
            if "Year" in col_name or "CIK" in col_name: # Assuming these are intended as numeric
                final_df[col_name] = pd.Series(pd.NA, index=transformed_df.index, dtype='Int64')
            elif "Date" in col_name:
                final_df[col_name] = pd.Series(pd.NaT, index=transformed_df.index, dtype='datetime64[ns]')
            else: # Default to object (string) type for others
                final_df[col_name] = pd.Series(None, index=transformed_df.index, dtype=object)
    
    logger.info(f"Data transformation completed. Output DataFrame shape: {final_df.shape}")
    logger.debug(f"Final columns in DataFrame: {final_df.columns.tolist()}")
    logger.debug(f"Sample of transformed data (first 3 rows):\n{final_df.head(3)}")
    
    return final_df