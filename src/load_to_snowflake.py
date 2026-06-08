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

def load_table_to_snowflake(source_table, target_table):
    """Read from Snowflake table and load to another table"""
    try:
        # Connect to Snowflake
        conn = connect_to_snowflake()
        
        # Read from source table
        query = f"SELECT id, name, sal FROM {source_table}"
        df = pd.read_sql(query, conn)  # Pass conn, not self.conn
        
        print(f"✓ Data loaded successfully. Shape: {df.shape}")
        
        # Write to target table
        success, nchunks, nrows, _ = write_pandas(
            conn, 
            df, 
            target_table.upper(),
            auto_create_table=True,
            overwrite=False
        )
        
        if success:
            print(f"✓ Successfully loaded {nrows} rows into {target_table}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage
    source_table = "inc_project"
    target_table = "test_snow"
    load_table_to_snowflake(source_table, target_table)
