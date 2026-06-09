import sqlite3
import os
import time
from datetime import datetime
import threading

# Path configuration
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "ebookstore.db")
ROOT_DIR = os.path.dirname(DB_DIR)

# SQLite Pragma settings for foreign keys
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    # Return dictionary rows
    conn.row_factory = sqlite3.Row
    return conn

# Thread-safe in-memory log for executed SQL queries
query_logs = []
query_logs_lock = threading.Lock()

def log_query(sql, params, duration_ms, status="SUCCESS"):
    with query_logs_lock:
        formatted_params = str(params) if params else ""
        query_logs.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "sql": sql.strip(),
            "params": formatted_params,
            "duration": round(duration_ms, 2),
            "status": status
        })
        # Cap logs at 100 items
        if len(query_logs) > 100:
            query_logs.pop(0)

def get_query_logs():
    with query_logs_lock:
        return list(reversed(query_logs))

def execute_read(query, params=None):
    """Executes a SELECT query and returns rows as dictionaries."""
    start_time = time.time()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        rows = cursor.fetchall()
        duration = (time.time() - start_time) * 1000
        log_query(query, params, duration)
        return [dict(row) for row in rows]
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        log_query(query, params, duration, status=f"ERROR: {str(e)}")
        raise e
    finally:
        conn.close()

def execute_write(query, params=None):
    """Executes an INSERT, UPDATE, or DELETE query."""
    start_time = time.time()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        lastrowid = cursor.lastrowid
        rowcount = cursor.rowcount
        duration = (time.time() - start_time) * 1000
        log_query(query, params, duration)
        return True, lastrowid, rowcount
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        log_query(query, params, duration, status=f"ERROR: {str(e)}")
        return False, str(e), 0
    finally:
        conn.close()

def execute_transaction(operations):
    """
    Executes multiple SQL operations inside a transaction.
    operations is a list of tuples: (query, params_tuple)
    """
    start_time = time.time()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        conn.execute("BEGIN TRANSACTION;")
        for query, params in operations:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
        conn.commit()
        duration = (time.time() - start_time) * 1000
        # Log combined transaction query
        log_query(" -- TRANSACTION -- \n" + "\n".join([op[0] for op in operations]), None, duration)
        return True, "Success"
    except Exception as e:
        conn.rollback()
        duration = (time.time() - start_time) * 1000
        log_query(" -- TRANSACTION ROLLBACK -- \n" + "\n".join([op[0] for op in operations]), None, duration, status=f"ROLLBACK ERROR: {str(e)}")
        return False, str(e)
    finally:
        conn.close()

# SQLite Schema Definitions
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS publishers (
    publisher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT,
    phone TEXT,
    website_url TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    bio TEXT,
    address TEXT,
    website_url TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT UNIQUE,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    publication_year INTEGER,
    description TEXT,
    publisher_id INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (publisher_id) REFERENCES publishers(publisher_id)
);

CREATE TABLE IF NOT EXISTS book_authors (
    book_id INTEGER,
    author_id INTEGER,
    is_primary_author INTEGER DEFAULT 0,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(author_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS book_categories (
    book_id INTEGER,
    category_id INTEGER,
    PRIMARY KEY (book_id, category_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    phone TEXT,
    role TEXT CHECK(role IN ('customer','admin','premium')) DEFAULT 'customer',
    address TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount REAL NOT NULL,
    status TEXT CHECK(status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')) DEFAULT 'pending',
    shipping_address TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS order_details (
    order_detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

CREATE TABLE IF NOT EXISTS shopping_cart (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    UNIQUE(customer_id, book_id)
);
"""

def init_db():
    """Initializes the database schema and seeds the initial data if new."""
    db_exists = os.path.exists(DB_PATH)
    
    conn = get_connection()
    try:
        # Create schema tables
        cursor = conn.cursor()
        cursor.executescript(SCHEMA_SQL)
        conn.commit()
        print("SQLite Database schema created/verified.")
        
        # Check if database is empty (e.g. check if publishers has records)
        cursor.execute("SELECT COUNT(*) FROM publishers")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Database is empty. Seeding initial data...")
            seed_data(conn)
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def seed_data(conn):
    """Reads ebookstore_insert_command.txt and executes statements inside a transaction."""
    insert_path = os.path.join(ROOT_DIR, "ebookstore_insert_command.txt")
    if not os.path.exists(insert_path):
        print(f"Seed file not found at {insert_path}. Seeding skipped.")
        return
        
    # Attempt to read seed file (handling potential UTF-16 encoding)
    content = ""
    encodings = ['utf-16', 'utf-8', 'latin-1']
    for enc in encodings:
        try:
            with open(insert_path, 'r', encoding=enc) as f:
                content = f.read()
                print(f"Successfully read seed file using {enc} encoding.")
                break
        except Exception:
            continue
            
    if not content:
        print("Failed to read the seed file with any supported encoding.")
        return
        
    # Parse insert statements
    cursor = conn.cursor()
    # Split by semicolon, filter empty commands
    statements = [stmt.strip() for stmt in content.split(";") if stmt.strip()]
    
    try:
        conn.execute("BEGIN TRANSACTION;")
        for stmt in statements:
            # Skip database switching commands if they are accidentally included
            if stmt.upper().startswith("USE ") or stmt.upper().startswith("CREATE DATABASE") or stmt.upper().startswith("DROP DATABASE"):
                continue
            cursor.execute(stmt)
        conn.commit()
        print("Successfully seeded all records from ebookstore_insert_command.txt!")
    except Exception as e:
        conn.rollback()
        print(f"Error seeding database: {e}")

# Run database initialization when imported
init_db()
