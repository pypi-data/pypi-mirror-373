from sqlalchemy import create_engine

def get_postgres_engine(connection_string):
    try:
        postgres_engine = create_engine(connection_string)
        return postgres_engine
    except Exception as e:
        print(f"Error creating PostgreSQL engine: {e}")
        raise

