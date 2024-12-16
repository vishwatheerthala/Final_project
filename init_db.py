import sqlite3

def initialize_db():
    """Sets up the initial schema for the restaurant database."""
    with sqlite3.connect("restaurant_data.db") as connection:  # Updated DB filename
        cursor = connection.cursor()

        # Table to store customer information
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                contact_number TEXT UNIQUE NOT NULL
            )
        """)

        # Table to store available menu items
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dish_name TEXT UNIQUE NOT NULL,
                cost REAL NOT NULL
            )
        """)

        # Table to store orders
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                order_notes TEXT,
                order_time INTEGER NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)

        # Table to store items in each order
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordered_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                menu_item_id INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES customer_orders(id),
                FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
            )
        """)

        print("Database schema initialized successfully.")

if __name__ == "__main__":
    initialize_db()
