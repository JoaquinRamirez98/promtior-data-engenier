import logging

# --- General Configuration ---
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

# --- Database Settings ---
DB_PATH = "data/sp500_companies.db" # Relative path to the SQLite database file
DB_TABLE_NAME = "companies"         # Name of the table to store company data

# --- Logging Configuration ---
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.DEBUG # Set to logging.INFO for less verbose output in production

# --- Data Extraction Configuration ---
# Defines the mapping between desired DataFrame column names (keys)
# and the exact text of the HTML table headers <th> (values) on Wikipedia.
# This mapping is crucial for robustly locating the correct data cells.
TABLE_COLUMN_MAPPING_KEYS = {
    "Symbol": "Symbol",
    "Security": "Security",
    "GICS_Sector": "GICS Sector",
    "GICS_Sub_Industry": "GICS Sub-Industry",
    "Headquarters_Location": "Headquarters Location",
    "Date_Added": "Date added",
    "CIK": "CIK",
    "Founded": "Founded"
}

# --- Data Transformation Configuration ---
# Defines the final set of columns expected in the DataFrame after transformation
# and to be loaded into the database.
FINAL_COLUMNS = [
    "Symbol", "Security", "GICS_Sector", "GICS_Sub_Industry",
    "Headquarters_City", "Headquarters_State", "Date_Added",
    "CIK", "Founded_Year"
]