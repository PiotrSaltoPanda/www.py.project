import sqlite3

# Połączenie z bazą danych (utworzy plik orders.db jeśli nie istnieje)
conn = sqlite3.connect('orders.db')
c = conn.cursor()

# Tworzymy tabelę orders jeśli nie istnieje
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

print("Tabela 'orders' gotowa!")
conn.commit()
conn.close()
