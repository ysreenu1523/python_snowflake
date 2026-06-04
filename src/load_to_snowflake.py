import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_snowflake_connection():
    """Establishes connection using environment variables for security."""
    try:
        conn = snowflake.connector.connect(
            user="YSREENUMBA",
            password="Manvitlasya@12",
            account="APJMMXT-GL29185",
            warehouse="DBTSNOW",
            database="DBTSNOW",
            schema="DBTSNOW"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        sys.exit(1)

def main():
    # Define paths relative to the script location
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'data', 'sample_data.csv')
    table_name = "sample" # Must match Snowflake case sensitivity rules

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)

    print(f"Reading data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Snowflake standardizes columns to uppercase unless double-quoted
    df.columns = [col.upper() for col in df.columns]

    print("Connecting to Snowflake...")
    conn = get_snowflake_connection()
    
    try:
        print(f"Uploading {len(df)} rows to table: {table_name}...")
        # auto_create_table=True creates the table if it does not exist
        success, nchunks, nrows, _ = write_pandas(
            conn, 
            df, 
            table_name.upper(),
            auto_create_table=True,
            overwrite=False
        )
        
        if success:
            print(f"✓ Successfully loaded {nrows} rows into {table_name}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage
    csv_path = "data\sample_data.csv"
    table_name = "MY_TABLE"
    
    load_csv_to_snowflake(csv_path, table_name)
