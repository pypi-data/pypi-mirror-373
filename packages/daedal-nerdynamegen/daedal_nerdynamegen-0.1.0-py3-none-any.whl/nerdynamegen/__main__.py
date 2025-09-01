"""
Main entry point for nerdynamegen package.
"""

from .dbconnsqlite import *


def main():
    """Main function to initialize the database and tables."""
    print("NerdyNameGen: Initializing database and tables...")
    print(f"Database created at: {db_path}")
    print("All tables created successfully!")


if __name__ == "__main__":
    main()
