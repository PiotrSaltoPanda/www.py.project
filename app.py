
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
# Inicjalizacja aplikacji Flask
app = Flask(__name__)
# Klucz do obsługi sesji (własny w prawdziwej aplikacji!)
app.secret_key = 'secret_key'
# Do bezpiecznego haszowania haseł
from werkzeug.security import generate_password_hash, check_password_hash

# --- RESETOWANIE HASŁA ---
# Użytkownik podaje e-mail i nowe hasło. Jeśli e-mail istnieje, hasło jest zmieniane.
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    message = None
    error = None
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        new_password = request.form.get('new_password')
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        if not user:
            error = 'Nie znaleziono użytkownika o podanym e-mailu.'
        else:
            hashed = generate_password_hash(new_password)
            c.execute('UPDATE users SET password = ? WHERE email = ?', (hashed, email))
            conn.commit()
            message = 'Hasło zostało zmienione. Możesz się teraz zalogować.'
        conn.close()
    return render_template('reset_password.html', message=message, error=error)
# --- DODAWANIE NOWEGO PRODUKTU (tylko admin) ---
@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_admin():
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price'))
        description = request.form.get('description')
        image = request.form.get('image')
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        c.execute('INSERT INTO products (name, price, description, image) VALUES (?, ?, ?, ?)',
                  (name, price, description, image))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_panel'))
    return render_template('add_product.html')

# --- EDYCJA PRODUKTU (tylko admin) ---
@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not is_admin():
        return redirect(url_for('home'))
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price'))
        description = request.form.get('description')
        image = request.form.get('image')
        c.execute('UPDATE products SET name=?, price=?, description=?, image=? WHERE id=?',
                  (name, price, description, image, product_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_panel'))
    c.execute('SELECT * FROM products WHERE id=?', (product_id,))
    product = c.fetchone()
    conn.close()
    return render_template('edit_product.html', product=product)

# --- USUWANIE PRODUKTU (tylko admin) ---
@app.route('/admin/delete_product/<int:product_id>')
def delete_product(product_id):
    if not is_admin():
        return redirect(url_for('home'))
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute('DELETE FROM products WHERE id=?', (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))
# --- PANEL ADMINA: zarządzanie produktami i zamówieniami ---
@app.route('/admin')
def admin_panel():
    # Sprawdź, czy użytkownik to admin
    if not is_admin():
        return redirect(url_for('home'))
    # Pobierz produkty z bazy
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    products = c.fetchall()
    conn.close()
    # Pobierz zamówienia z bazy
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('SELECT * FROM orders ORDER BY created_at DESC')
    orders = c.fetchall()
    conn.close()
    # Przekaż dane do szablonu admin_panel.html
    return render_template('admin_panel.html', products=products, orders=orders)

# --- REJESTRACJA UŻYTKOWNIKA ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        # Walidacja e-maila (prosty wzorzec)
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template('register.html', error='Podaj poprawny adres e-mail!')
        # Walidacja długości hasła
        if len(password) < 6:
            return render_template('register.html', error='Hasło musi mieć co najmniej 6 znaków!')
        # Sprawdź, czy użytkownik już istnieje
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        if user:
            conn.close()
            return render_template('register.html', error='Taki e-mail już istnieje!')
        # Zapisz nowego użytkownika z haszowanym hasłem
        hashed = generate_password_hash(password)
        c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# --- LOGOWANIE UŻYTKOWNIKA ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        # Walidacja e-maila (prosty wzorzec)
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template('login.html', error='Podaj poprawny adres e-mail!')
        # Walidacja długości hasła
        if len(password) < 6:
            return render_template('login.html', error='Hasło musi mieć co najmniej 6 znaków!')
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT id, password FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['user_email'] = email
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Nieprawidłowy e-mail lub hasło!')
    return render_template('login.html')

# --- WYLOGOWANIE UŻYTKOWNIKA ---
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    return redirect(url_for('home'))

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
# Klucz do obsługi sesji (własny w prawdziwej aplikacji!)
app.secret_key = 'secret_key'

# --- FUNKCJE POMOCNICZE ---

# Pobierz wszystkie produkty z bazy SQLite
def get_all_products():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row  # Pozwala na dostęp do kolumn po nazwie
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    rows = c.fetchall()
    products = []
    for row in rows:
        products.append({
            'id': row['id'],
            'name': row['name'],
            'price': row['price'],
            'description': row['description'],
            'image': row['image']
        })
    conn.close()
    return products

# Pobierz pojedynczy produkt po id
def get_product_by_id(product_id):
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row['id'],
            'name': row['name'],
            'price': row['price'],
            'description': row['description'],
            'image': row['image']
        }
    return None

# --- TRASY APLIKACJI ---

# Strona główna: produkty z bazy
@app.route('/')
def home():
    products = get_all_products()
    return render_template('index.html', products=products)

# Koszyk: produkty z bazy na podstawie id z sesji
@app.route('/cart')
def cart():
    cart = session.get('cart', {})  # Słownik: {product_id: ilość}
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = get_product_by_id(int(pid))
        if product:
            item = product.copy()
            item['quantity'] = qty
            item['subtotal'] = qty * product['price']
            cart_items.append(item)
            total += item['subtotal']
    return render_template('cart.html', cart_items=cart_items, total=total)

# Dodawanie produktu do koszyka (sprawdzenie czy istnieje w bazie)
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form.get('product_id'))
    if not get_product_by_id(product_id):
        return "Produkt nie istnieje", 404
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    return redirect(url_for('cart'))

# Usuwanie produktu z koszyka
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = str(request.form.get('product_id'))
    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
    session['cart'] = cart
    return redirect(url_for('cart'))

# Zmiana ilości produktu w koszyku
@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    product_id = str(request.form.get('product_id'))
    try:
        quantity = int(request.form.get('quantity'))
    except (TypeError, ValueError):
        quantity = 1
    cart = session.get('cart', {})
    if quantity > 0:
        cart[product_id] = quantity
    else:
        cart.pop(product_id, None)
    session['cart'] = cart
    return redirect(url_for('cart'))

# Obsługa zamówienia z koszyka (zapis do bazy orders.db)
@app.route('/order', methods=['POST'])
def order():
    # Pobierz dane z formularza
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    street = request.form.get('street')
    street2 = request.form.get('street2')
    number = request.form.get('number')
    postcode = request.form.get('postcode')
    city = request.form.get('city')
    country = request.form.get('country')
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = get_product_by_id(int(pid))
        if product:
            item = product.copy()
            item['quantity'] = qty
            item['subtotal'] = qty * product['price']
            cart_items.append(item)
            total += item['subtotal']
    # Zapisz zamówienie do bazy SQLite
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''INSERT INTO orders (name, email, phone, street, street2, number, postcode, city, country, products, total)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (name, email, phone, street, street2, number, postcode, city, country,
               str([{'name': item['name'], 'quantity': item['quantity'], 'subtotal': item['subtotal']} for item in cart_items]),
               total))
    conn.commit()
    conn.close()
    session['cart'] = {}
    return f"<h2>Dziękujemy za zamówienie, {name}!</h2><p>Potwierdzenie wysłaliśmy na: {email}</p><p>Wróć do <a href='/'>sklepu</a>."


# --- PANEL ADMINA: ochrona dostępu ---
# Panel zamówień dostępny tylko dla admina (np. e-mail: admin@shop.com)
def is_admin():
    # Możesz zmienić e-mail admina na dowolny inny
    return session.get('user_email') == 'admin@shop.com'

@app.route('/orders')
def show_orders():
    if not is_admin():
        # Jeśli nie admin, przekieruj na stronę główną lub pokaż błąd
        return redirect(url_for('home'))
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email, phone, street, street2, number, postcode, city, country, products, total, created_at FROM orders ORDER BY created_at DESC')
    orders = c.fetchall()
    conn.close()
    return render_template('orders.html', orders=orders)

# Prosta trasa testowa
@app.route('/test')
def test():
    return "Test works!"

# Uruchom aplikację tylko jeśli plik jest uruchamiany bezpośrednio
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

# Tworzymy główny obiekt aplikacji Flask
app = Flask(__name__)
app.secret_key = 'secret_key'  # Klucz do obsługi sesji (zmień na własny w prawdziwej aplikacji)

# Podstrona koszyka
@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        # Znajdź produkt po id
        product = next((p for p in products if p['id'] == int(pid)), None)
        if product:
            item = product.copy()
            item['quantity'] = qty
            item['subtotal'] = qty * product['price']
            cart_items.append(item)
            total += item['subtotal']
    return render_template('cart.html', cart_items=cart_items, total=total)

# Lista produktów do wyświetlenia na stronie głównej
products = [
    {
        "id": 1,
        "name": "Sleeping Panda",
        "price": 99.00,
        "description": "This exceptional panda is always sleepy; you can always count on it when you want to cuddle up to someone and fall asleep. Perfect as a gift or for everyday use!",
        "image": "/static/images/needmorecoffee.jpeg"
    },
    {
        "id": 2,
        "name": "Clean Panda",
        "price": 99.00,
        "description": "This is a special panda that tries to keep the apartment tidy, although it doesn't always succeed. However, it is so adorable that it doesn't have to!",
        "image": "/static/images/IMG_4589.jpg"  # Dodaj to zdjęcie do folderu static/images
    },
    {
        "id": 3,
        "name": "Hungry Panda",
        "price": 99.00,
        "description": "This is a special panda, the Charming Panda, who is always hungry and will help you prepare a delicious and hearty meal!",
        "image": "/static/images/IMG_4592.jpg"  # Dodaj to zdjęcie do folderu static/images
    }
]

@app.route('/')
def home():
    return render_template('index.html', products=products)


# Dodajemy trasę do dodawania produktu do koszyka
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form.get('product_id'))
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    return redirect(url_for('cart'))

# Obsługa zamówienia z koszyka (POST)
@app.route('/order', methods=['POST'])
def order():
    # Pobierz dane z formularza
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    street = request.form.get('street')
    street2 = request.form.get('street2')
    number = request.form.get('number')
    postcode = request.form.get('postcode')
    city = request.form.get('city')
    country = request.form.get('country')
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = next((p for p in products if p['id'] == int(pid)), None)
        if product:
            item = product.copy()
            item['quantity'] = qty
            item['subtotal'] = qty * product['price']
            cart_items.append(item)
            total += item['subtotal']
    # Zapisz zamówienie do bazy SQLite
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''INSERT INTO orders (name, email, phone, street, street2, number, postcode, city, country, products, total)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (name, email, phone, street, street2, number, postcode, city, country,
               str([{'name': item['name'], 'quantity': item['quantity'], 'subtotal': item['subtotal']} for item in cart_items]),
               total))
    conn.commit()
    conn.close()
    session['cart'] = {}
    return f"<h2>Dziękujemy za zamówienie, {name}!</h2><p>Potwierdzenie wysłaliśmy na: {email}</p><p>Wróć do <a href='/'>sklepu</a>.</p>"

# Panel admina: odczyt zamówień z bazy SQLite (GET)
@app.route('/orders')
def show_orders():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email, phone, street, street2, number, postcode, city, country, products, total, created_at FROM orders ORDER BY created_at DESC')
    orders = c.fetchall()
    conn.close()
    # Przekazujemy zamówienia do szablonu Jinja2 (orders.html)
    return render_template('orders.html', orders=orders)

@app.route('/test')
def test():
    return "Test works!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
