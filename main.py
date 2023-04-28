import os

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    url_for,
    render_template,
    request,
    redirect,
    session,
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_paginate import Pagination
from sqlalchemy import func
import stripe

from bot import send_message
from forms import ContactForm


PER_PAGE = 16

load_dotenv()

stripe.api_key = os.environ['STRIPE_KEY']
PRICE_30 = os.environ['PRICE_30']
PRICE_50 = os.environ['PRICE_50']

app = Flask(__name__)
PASSWORD = os.environ['PSGL_PASS']

app.config[
    'SQLALCHEMY_DATABASE_URI'
] = f'postgresql://postgres:{PASSWORD}@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CSRF_ENABLED'] = True
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.secret_key = os.environ['FLASK_KEY']


db = SQLAlchemy(app)
migrate = Migrate(app, db)

USER_ID = 'user_id'


class Item(db.Model):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(20), nullable=False)
    model = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    question = db.Column(db.Text, nullable=False)


@app.route('/')
@app.route('/<int:page>')
@app.route('/<string:brand>')
@app.route('/<string:brand>/<int:page>')
def index(brand=None, page=1):
    cart = session.get('cart', [])
    offset = (page - 1) * PER_PAGE
    if brand:
        data = (
            Item.query.filter(Item.brand == brand)
            .limit(PER_PAGE)
            .offset(offset)
            .all()
        )
        total = Item.query.filter(Item.brand == brand).count()
    else:
        data = Item.query.limit(PER_PAGE).offset(offset).all()
        total = Item.query.count()
    pagination = Pagination(
        page=page,
        per_page=PER_PAGE,
        total=total,
        # link_size=1,
        # prev_label='<',
        # next_label='>',
        outer_window=0,
        inner_window=1,
    )
    pagination.current_page_fmt = '<li class="page-item active"><a class="page-link">{0}<span class="sr-only"></span></a></li>'
    pagination.gap_marker_fmt = ''
    return render_template(
        'index.html',
        cards=data,
        item_qty=len(cart),
        pagination=pagination,
    )


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_id = request.form['item_id']
    item_number = request.form['item_number']
    description = request.form['item_description']
    item_price = request.form['item_price']
    cart = session.get('cart', [])
    last_page = request.referrer
    for item in cart:
        if item.get('id') == item_id:
            flash('You already have this item in cart!', 'error')
            return redirect(last_page)
    cart.append(
        {
            'id': item_id,
            'price': item_price,
            'number': item_number,
            'description': description,
        }
    )
    session['cart'] = cart

    flash('Item has been added to cart!')

    return redirect(last_page)


@app.route('/details/<int:item_id>')
def details(item_id):
    item = Item.query.get(item_id)
    cart = session.get('cart', [])
    related = (
        Item.query.filter(Item.model == item.model)
        .filter(Item.id != item_id)
        .all()
    )
    return render_template(
        'details.html', item=item, item_qty=len(cart), related=related
    )


@app.route('/checkout')
def checkout():
    total = 0
    items = session.get('cart', [])
    if items:
        total = sum([int(item.get('price')) for item in items])

    return render_template(
        'checkout.html', items=items, item_qty=len(items), total=total
    )


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    cart = session.get('cart', [])
    form = ContactForm()
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        question = form.question.data

        new_question = User(name=name, email=email, question=question)
        db.session.add(new_question)
        db.session.commit()
        send_message(
            f'Новый вопрос от: {name}!\nПочта: {email}\nВопрос: {question}'
        )
        flash(
            'Your question has been sent successfully! We will get in touch as soon as possible!'
        )

        return redirect(url_for('contact'))
    return render_template('contact.html', form=form, item_qty=len(cart))


@app.route('/about')
def about():
    cart = session.get('cart', [])

    return render_template('about.html', item_qty=len(cart))


@app.route('/success')
def success():
    session['cart'] = []
    session_id = request.args.get('session_id')
    try:
        payment_intent_id = stripe.checkout.Session.retrieve(
            session_id
        ).payment_intent

        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        payment_method = stripe.PaymentMethod.retrieve(
            payment_intent.payment_method
        )
        email = payment_method.get('billing_details').get('email')

        send_message(f'Новый заказ оплачен!\nПочта: {email}')
    except Exception as e:
        send_message(
            'Новый заказ поступил, но не удалось найти его параметры. Ищи в базе'
        )
        send_message(f'Ошибка обработки данных: {e}')

    return render_template('success.html')


@app.route('/cancel')
def cancel():
    cart = session.get('cart', [])

    return render_template('cancel.html', item_qty=len(cart))


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    prices = request.form.getlist('price')
    items = session.get('cart', [])
    line_items = []
    for price in prices:
        if int(price) == 30:
            line_items.append({'price': PRICE_30, 'quantity': 1})
        elif int(price) == 50:
            line_items.append({'price': PRICE_50, 'quantity': 1})

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=url_for('success', _external=True)
            + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('cancel', _external=True),
        )

    except Exception as e:
        return str(e)
    send_message(message=f'Начата оплата!\nТовары: {items}')
    return redirect(checkout_session.url, code=303)


@app.route('/search', methods=['POST', 'GET'])
def search():
    cart = session.get('cart', [])
    if request.method == 'GET':
        query = session.get('query')

    else:
        query = request.form.get('query')
    aggregate = Item.query.filter(
        func.replace(func.replace(func.lower(Item.number), '-', ''), ' ', '')
        == func.replace(func.lower(f'{query}'), '-', '')
    )
    files = aggregate.all()
    total = aggregate.count()
    pagination = Pagination(
        page=1,
        per_page=PER_PAGE,
        total=total,
    )
    session['query'] = query

    return render_template(
        'index.html', cards=files, pagination=pagination, item_qty=len(cart)
    )


@app.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):
    items = session.get('cart', [])
    for i in range(len(items)):
        if int(items[i].get('id')) == item_id:
            items.pop(i)
            break
    session['cart'] = items

    total = 0
    if items:
        total = sum([int(item.get('price')) for item in items])

    return render_template(
        'checkout.html', items=items, item_qty=len(items), total=total
    )


@app.route('/google91b4364c93644c83.html')
def google():
    return render_template('google91b4364c93644c83.html')


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port='5000')
