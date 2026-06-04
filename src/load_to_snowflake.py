import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def connect_to_snowflake():
    """Establish connection to Snowflake"""
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA')
    )
    return conn

def load_csv_to_snowflake(csv_file_path, table_name):
    """Read CSV and load to Snowflake"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        
        print(f"✓ CSV loaded successfully. Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Connect to Snowflake
        conn = connect_to_snowflake()
        
        # Write to Snowflake
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
    csv_path = "data/sample_data.csv"
    table_name = "MY_TABLE"
    
    load_csv_to_snowflake(csv_path, table_name)
