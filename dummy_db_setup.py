import psycopg2
from psycopg2.extras import execute_batch
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def create_schema(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sales (
            voucher_no TEXT PRIMARY KEY,
            voucher_date DATE NOT NULL,
            customer_id INTEGER REFERENCES customers(id),
            customer_name TEXT,
            total_amount NUMERIC
        );

        CREATE TABLE IF NOT EXISTS sales_items (
            id SERIAL PRIMARY KEY,
            voucher_no TEXT REFERENCES sales(voucher_no) ON DELETE CASCADE,
            item_name TEXT NOT NULL,
            quantity INTEGER,
            rate NUMERIC,
            amount NUMERIC
        );

        CREATE TABLE IF NOT EXISTS stock_items (
            item_name TEXT PRIMARY KEY,
            opening_qty INTEGER
        );

        CREATE TABLE IF NOT EXISTS stock_movements (
            id SERIAL PRIMARY KEY,
            item_name TEXT REFERENCES stock_items(item_name),
            movement_type TEXT CHECK (movement_type IN ('IN', 'OUT')),
            quantity INTEGER,
            movement_date DATE
        );
        """)
        conn.commit()
        print("✅ Schema created successfully")

def insert_dummy_data(conn):
    with conn.cursor() as cur:

        # CUSTOMERS
        cur.execute("""
        INSERT INTO customers (id, name)
        VALUES
        (1, 'Rahul Sharma'),
        (2, 'Anita Verma'),
        (3, 'TechNova Pvt Ltd')
        ON CONFLICT (id) DO NOTHING;
        """)

        # SALES
        cur.execute("""
        INSERT INTO sales (voucher_no, voucher_date, customer_id, customer_name, total_amount)
        VALUES
        ('VCH001', '2026-01-01', 1, 'Rahul Sharma', 15000),
        ('VCH002', '2026-01-02', 2, 'Anita Verma', 8200),
        ('VCH003', '2026-01-03', 3, 'TechNova Pvt Ltd', 45500)
        ON CONFLICT (voucher_no) DO NOTHING;
        """)

        # SALES ITEMS
        sales_items_data = [
            ('VCH001', 'CCTV Camera', 2, 5000, 10000),
            ('VCH001', 'Hard Disk 1TB', 1, 5000, 5000),
            ('VCH002', 'WiFi Camera', 1, 3200, 3200),
            ('VCH002', 'Memory Card 128GB', 2, 2500, 5000),
            ('VCH003', 'CCTV Camera', 5, 4800, 24000),
            ('VCH003', 'NVR 8 Channel', 1, 12000, 12000),
            ('VCH003', 'Hard Disk 2TB', 1, 9500, 9500),
        ]

        execute_batch(cur, """
        INSERT INTO sales_items (voucher_no, item_name, quantity, rate, amount)
        VALUES (%s, %s, %s, %s, %s);
        """, sales_items_data)

        # STOCK ITEMS
        cur.execute("""
        INSERT INTO stock_items (item_name, opening_qty)
        VALUES
        ('CCTV Camera', 50),
        ('WiFi Camera', 30),
        ('Hard Disk 1TB', 20),
        ('Hard Disk 2TB', 15),
        ('NVR 8 Channel', 10),
        ('Memory Card 128GB', 40)
        ON CONFLICT (item_name) DO NOTHING;
        """)

        # STOCK MOVEMENTS
        stock_movements_data = [
            ('CCTV Camera', 'OUT', 2, '2026-01-01'),
            ('Hard Disk 1TB', 'OUT', 1, '2026-01-01'),
            ('WiFi Camera', 'OUT', 1, '2026-01-02'),
            ('Memory Card 128GB', 'OUT', 2, '2026-01-02'),
            ('CCTV Camera', 'OUT', 5, '2026-01-03'),
            ('NVR 8 Channel', 'OUT', 1, '2026-01-03'),
            ('Hard Disk 2TB', 'OUT', 1, '2026-01-03'),
            ('CCTV Camera', 'IN', 20, '2026-01-05'),
            ('WiFi Camera', 'IN', 10, '2026-01-05'),
        ]

        execute_batch(cur, """
        INSERT INTO stock_movements (item_name, movement_type, quantity, movement_date)
        VALUES (%s, %s, %s, %s);
        """, stock_movements_data)

        conn.commit()
        print("✅ Dummy data inserted successfully")

def main():
    conn = get_connection()
    try:
        create_schema(conn)
        insert_dummy_data(conn)
    finally:
        conn.close()
        print("🔌 Database connection closed")

if __name__ == "__main__":
    main()
