import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import getpass

def init_db():
    print("=== PostgreSQL Database Initialization ===")
    print("Please enter your PostgreSQL password for the default 'postgres' user.")
    pg_password = getpass.getpass(prompt='Password: ')
    
    db_name = "agentic_rag"
    
    # 1. Connect to the default 'postgres' database to create the new one
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password=pg_password,
            host="localhost",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name}")
        else:
            print(f"Database '{db_name}' already exists.")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return

    # 2. Connect to the new 'agentic_rag' database and create tables
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user="postgres",
            password=pg_password,
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        print("Creating tables...")
        
        # Table: Schemas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schemas (
                schema_name VARCHAR(255) PRIMARY KEY,
                problem_domain VARCHAR(255),
                description TEXT,
                raw_json TEXT
            )
        """)
        
        # Table: Schema Classes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_classes (
                id SERIAL PRIMARY KEY,
                schema_name VARCHAR(255) REFERENCES schemas(schema_name),
                class_name VARCHAR(255),
                data_source VARCHAR(255),
                date_aggregation_on VARCHAR(255),
                settlement_type VARCHAR(255),
                output_process_code VARCHAR(255),
                computation_type VARCHAR(255),
                raw_class_json TEXT,
                UNIQUE(schema_name, class_name)
            )
        """)
        
        # Table: Conditions (C2)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conditions (
                id SERIAL PRIMARY KEY,
                class_id INTEGER REFERENCES schema_classes(id),
                field_name VARCHAR(255),
                value_pattern VARCHAR(255),
                equality_operator VARCHAR(50)
            )
        """)
        
        # Table: Components (C3)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS components (
                id SERIAL PRIMARY KEY,
                class_id INTEGER REFERENCES schema_classes(id),
                component_name VARCHAR(255),
                model_id VARCHAR(255),
                type VARCHAR(50),
                component_type VARCHAR(50),
                component_expr TEXT
            )
        """)
        
        # Table: Criteria (C4)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS criteria (
                id SERIAL PRIMARY KEY,
                component_id INTEGER REFERENCES components(id),
                field_name VARCHAR(255),
                value_pattern VARCHAR(255),
                equality_operator VARCHAR(50)
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialization complete! Tables created successfully.")
        
        # Save password to .env for future scripts so you don't have to type it again
        with open(".env", "a") as f:
            f.write(f"\nPG_USER=postgres\nPG_PASSWORD={pg_password}\nPG_DB={db_name}\nPG_HOST=localhost\nPG_PORT=5432\n")
        print("Credentials saved to .env file.")
        
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    init_db()
