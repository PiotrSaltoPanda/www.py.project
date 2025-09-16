import sqlite3

# Połączenie z bazą danych (utworzy plik users.db jeśli nie istnieje)
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Tworzymy tabelę users jeśli nie istnieje
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

print("Tabela 'users' gotowa!")
conn.commit()
conn.close()
