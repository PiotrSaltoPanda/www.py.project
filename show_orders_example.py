from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/order', methods=['POST'])
def order():
    name = request.form.get('name')
    email = request.form.get('email')
    address = request.form.get('address')
    # Zapisz zamówienie do pliku tekstowego
    with open('orders.txt', 'a', encoding='utf-8') as f:
        f.write(f"Imię i nazwisko: {name}\nE-mail: {email}\nAdres: {address}\n---\n")
    return f"Dziękujemy za zamówienie, {name}!<br>Potwierdzenie wysłaliśmy na: {email}<br>Adres wysyłki: {address}"

@app.route('/orders')
def show_orders():
    try:
        with open('orders.txt', 'r', encoding='utf-8') as f:
            orders = f.read().replace('\n', '<br>')
    except FileNotFoundError:
        orders = 'Brak zamówień.'
    return f'<h2>Lista zamówień:</h2><div style="white-space:pre-line">{orders}</div>'
