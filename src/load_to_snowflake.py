import os
import pandas as pd
from sqlalchemy import create_engine
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import urllib.parse
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

def get_snowflake_engine_and_conn():
    """Establish SQLAlchemy engine and raw connection for Snowflake"""
    user = os.getenv('SNOWFLAKE_USER')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
    database = os.getenv('SNOWFLAKE_DATABASE')
    schema = os.getenv('SNOWFLAKE_SCHEMA')

    safe_password = urllib.parse.quote_plus(os.getenv('SNOWFLAKE_PASSWORD'))
    safe_user = urllib.parse.quote_plus(os.getenv('SNOWFLAKE_USER'))
    # 1. Create SQLAlchemy Engine to eliminate the pd.read_sql warning
    connection_url = f"snowflake://{safe_user}:{safe_password}@{account}/{database}/{schema}?warehouse={warehouse}"
    engine = create_engine(connection_url)
    
    # 2. Create raw connection needed specifically for write_pandas
    raw_conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        database=database,
        schema=schema
    )
    
    return engine,  raw_conn

def load_table_to_snowflake(source_table, target_table):
    """Read from Snowflake table using Engine and load to another table using raw conn"""
    raw_conn = None
    try:
        # Get both connectables
        engine, raw_conn = get_snowflake_engine_and_conn()
        
        # Read from source table using the SQLAlchemy engine context
        query = f"SELECT id, name, sal FROM {source_table}"
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        print(f"✓ Data loaded successfully. Shape: {df.shape}")
        
        # Snowflake requires uppercase column names for write_pandas to match target tables correctly
        df.columns = [col.upper() for col in df.columns]
        
        # Write to target table using the raw connection
        success, nchunks, nrows, _ = write_pandas(
            conn=raw_conn, 
            df=df, 
            table_name=target_table.upper(),
            auto_create_table=True,
            overwrite=False
        )
        
        if success:
            print(f"✓ Successfully loaded {nrows} rows into {target_table}")
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False
        
    finally:
        # Ensure connection closes even if an error occurs
        if raw_conn:
            raw_conn.close()

if __name__ == "__main__":
    # Example usage
    source_table = "inc_project"
    target_table = "test_snow"
    load_table_to_snowflake(source_table, target_table)