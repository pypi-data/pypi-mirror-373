import sqlite3

def initialize_database():
    """
    Initialize SQLite database with necessary tables.
    """
    conn = sqlite3.connect('context_database.db')
    cursor = conn.cursor()

    # Table for storing query-answer pairs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

    # Table for storing web search results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS web_search_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            results TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

    conn.commit()
    conn.close()
