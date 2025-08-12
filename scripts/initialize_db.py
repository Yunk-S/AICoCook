import os
import sys
from sqlalchemy import create_engine

# Add the project root to the Python path to allow for absolute imports
# This is a bit of a hack to make the script runnable from the root directory
# A more robust solution would be to make this a proper CLI command within the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'aire-backend')))

from app.database import Base
from app.core.config import settings

def initialize_database():
    """
    Creates all database tables based on the SQLAlchemy models.
    """
    print("Connecting to the database...")
    
    # We need to construct the absolute path for the SQLite database
    # The path in settings is relative to the `aire-backend/app` directory
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'aire_local.db'))
    db_url = f"sqlite:///{db_path}"

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    
    print(f"Database URL: {db_url}")
    print("Creating all tables... (This might take a moment)")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("Successfully created all tables.")
    except Exception as e:
        print(f"An error occurred while creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("--- Starting Database Initialization ---")
    initialize_database()
    print("--- Database Initialization Finished ---")
