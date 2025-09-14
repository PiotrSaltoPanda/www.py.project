import sqlite3

def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            street TEXT,
            street2 TEXT,
            number TEXT,
            postcode TEXT,
            city TEXT,
            country TEXT,
            products TEXT,
            total REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Baza danych orders.db i tabela orders zostały utworzone.")
