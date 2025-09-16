import sqlite3

# Połączenie z bazą danych (utworzy plik products.db jeśli nie istnieje)
conn = sqlite3.connect('products.db')
c = conn.cursor()

# Tworzymy tabelę products jeśli nie istnieje
c.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    image TEXT
)
''')

# Przykładowe produkty (możesz dodać więcej lub zmienić)
products = [
    ("Sleeping Panda", 99.00, "This exceptional panda is always sleepy; you can always count on it when you want to cuddle up to someone and fall asleep. Perfect as a gift or for everyday use!", "/static/images/needmorecoffee.jpeg"),
    ("Clean Panda", 99.00, "This is a special panda that tries to keep the apartment tidy, although it doesn't always succeed. However, it is so adorable that it doesn't have to!", "/static/images/IMG_4589.jpg"),
    ("Hungry Panda", 99.00, "This is a special panda, the Charming Panda, who is always hungry and will help you prepare a delicious and hearty meal!", "/static/images/IMG_4592.jpg")
]

# Wstawiamy produkty tylko jeśli tabela jest pusta
c.execute('SELECT COUNT(*) FROM products')
if c.fetchone()[0] == 0:
    c.executemany('INSERT INTO products (name, price, description, image) VALUES (?, ?, ?, ?)', products)
    print("Dodano przykładowe produkty do bazy.")
else:
    print("Produkty już istnieją w bazie.")

conn.commit()
conn.close()
print("Baza danych gotowa!")
