import duckdb
import os
import uuid
import pandas as pd
from app.models.data_schema import DatasetSchema, ColumnSchema

# Use a persistent DuckDB file so the Docker sandbox can mount and read it
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data.duckdb'))
conn = duckdb.connect(database=DB_PATH)

def load_file_to_duckdb(file_path: str, file_name: str) -> str:
    """
    Loads a CSV or Excel file into the DuckDB instance.
    Returns the generated table name.
    """
    # Generate a unique table name
    table_name = f"dataset_{uuid.uuid4().hex[:8]}"
    
    # Check file extension to determine loading method
    _, ext = os.path.splitext(file_name)
    ext = ext.lower()
    
    try:
        if ext == '.csv':
            # DuckDB can natively read CSVs
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_path}')")
        elif ext in ['.xls', '.xlsx']:
            # For Excel, load via pandas first
            df = pd.read_excel(file_path)
            # Register dataframe as a view, then create table
            conn.register('temp_df', df)
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM temp_df")
            conn.unregister('temp_df')
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        return table_name
    except Exception as e:
        raise RuntimeError(f"Failed to load file into DuckDB: {str(e)}")

def extract_schema(table_name: str) -> DatasetSchema:
    """
    Extracts column names, data types, and 5 sample rows from the specified table.
    """
    # Get schema
    schema_query = f"DESCRIBE {table_name}"
    schema_df = conn.execute(schema_query).fetchdf()
    
    columns = []
    for _, row in schema_df.iterrows():
        columns.append(ColumnSchema(
            name=row['column_name'],
            data_type=row['column_type']
        ))
        
    # Get 5 sample rows
    sample_query = f"SELECT * FROM {table_name} LIMIT 5"
    sample_df = conn.execute(sample_query).fetchdf()
    
    # Convert dates/timestamps to string for JSON serialization if necessary,
    # but pandas to_dict usually handles basic types. We use records format.
    sample_data = sample_df.to_dict(orient='records')
    
    return DatasetSchema(
        table_name=table_name,
        columns=columns,
        sample_data=sample_data
    )
