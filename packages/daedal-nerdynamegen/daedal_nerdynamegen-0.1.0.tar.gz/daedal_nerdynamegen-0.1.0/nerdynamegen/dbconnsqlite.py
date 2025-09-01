## License
# This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

import os
import sqlite3


# Create a sqlite database and tables for the name generator
def create_sqlite_db(db_path):
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.close()


def create_namelist_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS namelist (
            uniquid INTEGER PRIMARY KEY AUTOINCREMENT,
            name CHAR(40),
            category CHAR(20),
            is_in_use BOOLEAN DEFAULT 0,
            is_in_use_since DATE
        )
    """
    )
    conn.commit()
    conn.close()


def create_character_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS character (
            uniquid INTEGER PRIMARY KEY AUTOINCREMENT,
            name CHAR(40) UNIQUE,
            description CHAR(200),
            source CHAR(40),
            type CHAR(20)
        )
    """
    )
    conn.commit()
    conn.close()


def create_phrase_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS phrase (
            uniquid INTEGER PRIMARY KEY AUTOINCREMENT,
            verb CHAR(40),
            adj CHAR(20),
            UNIQUE(verb, adj)
        )
    """
    )
    conn.commit()
    conn.close()


def create_place_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS place (
            uniquid INTEGER PRIMARY KEY AUTOINCREMENT,
            name CHAR(40) UNIQUE,
            description CHAR(200),
            source CHAR(40),
            type CHAR(20)
        )
    """
    )
    conn.commit()
    conn.close()


db_path = os.path.join(os.path.dirname(__file__), "nerdynamegen.db")
create_sqlite_db(db_path)
create_namelist_table()
create_character_table()
create_place_table()
create_phrase_table()
