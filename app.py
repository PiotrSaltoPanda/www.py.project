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
    html = '<h2>Lista zamówień (panel admina)</h2>'
    if not orders:
        html += '<p>Brak zamówień.</p>'
    else:
        html += '<table border="1" cellpadding="5"><tr><th>ID</th><th>Data</th><th>Imię i nazwisko</th><th>Email</th><th>Telefon</th><th>Adres</th><th>Produkty</th><th>Suma</th></tr>'
        for o in orders:
            html += f'<tr><td>{o[0]}</td><td>{o[12]}</td><td>{o[1]}</td><td>{o[2]}</td><td>{o[3]}</td>'
            html += f'<td>{o[4]} {o[5]} {o[6]}, {o[7]} {o[8]}, {o[9]}</td>'
            html += f'<td><pre style="white-space:pre-line">{o[10]}</pre></td><td>{o[11]} zł</td></tr>'
        html += '</table>'
    html += '<p><a href="/">Powrót do sklepu</a></p>'
    return html

@app.route('/test')
def test():
    return "Test działa!"
