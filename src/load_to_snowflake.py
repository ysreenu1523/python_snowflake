import os
import sys
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

def get_snowflake_connection():
    """Establishes connection using environment variables for security."""
    try:
        conn = snowflake.connector.connect(
            user="YSREENUMBA",
            password="*******",
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
            conn=conn,
            df=df,
            table_name=table_name,
            auto_create_table=True
        )
        
        if success:
            print(f"Successfully loaded {nrows} rows into Snowflake across {nchunks} chunks.")
        else:
            print("Data load failed.")
            
    except Exception as e:
        print(f"Database operation failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
