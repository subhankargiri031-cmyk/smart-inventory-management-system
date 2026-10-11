import hashlib
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Subha@1234",
    "database": "smart_inventory"
}

def connect_db():
    """Create and return a connection to the application database."""
    return mysql.connector.connect(**DB_CONFIG)

def password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def initialize_database():
    """Create tables if needed and ensure the default login exists."""
    con = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cur = con.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS smart_inventory")
    cur.execute("USE smart_inventory")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash CHAR(64) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INT AUTO_INCREMENT PRIMARY KEY,
            category_name VARCHAR(100) NOT NULL UNIQUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INT AUTO_INCREMENT PRIMARY KEY,
            supplier_name VARCHAR(100) NOT NULL,
            phone VARCHAR(25),
            email VARCHAR(100),
            address VARCHAR(255)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            product_name VARCHAR(120) NOT NULL,
            category_id INT NULL,
            supplier_id INT NULL,
            quantity INT NOT NULL DEFAULT 0,
            purchase_price DECIMAL(10,2) NOT NULL DEFAULT 0,
            selling_price DECIMAL(10,2) NOT NULL DEFAULT 0,
            low_stock_level INT NOT NULL DEFAULT 5,
            expiry_date DATE NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
                ON DELETE SET NULL ON UPDATE CASCADE,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
                ON DELETE SET NULL ON UPDATE CASCADE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
                ON DELETE RESTRICT ON UPDATE CASCADE
        )
    """)
    cur.execute("INSERT IGNORE INTO categories (category_name) VALUES "
                "('Computer Accessories'), ('Electronics'), ('Office Supplies')")
    cur.execute("""
        INSERT IGNORE INTO suppliers (supplier_name, phone, email, address)
        VALUES ('ABC Suppliers', '9876543210', 'abc@example.com', 'Bhubaneswar'),
               ('Tech World', '9123456780', 'tech@example.com', 'Cuttack')
    """)
    cur.execute("SELECT user_id FROM users WHERE username=%s", ("admin",))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            ("admin", password_hash("admin123"))
        )
    con.commit()
    cur.close()
    con.close()

def check_login(username, password):
    con = connect_db()
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT user_id FROM users WHERE username=%s AND password_hash=%s",
            (username, password_hash(password))
        )
        result = cur.fetchone()
        cur.close()
        return result is not None
    finally:
        con.close()
