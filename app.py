from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
import mysql.connector


db = mysql.connector.connect(
  host="162.241.2.234",
  user="ghclim06_api",
  passwd="Guedes123",
  database="ghclim06_mercado_facil"
)

app = Flask(__name__)

jwt = JWTManager(app)

app.config['JWT_SECRET_KEY'] = "777eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9ovos"
app.config['JWT_HEADER_TYPE'] = ""


@app.route('/login', methods=['POST'])
def login():
    email = request.get_json()['email']
    password = request.get_json()['password']

    cursor = db.cursor()
    sql = "SELECT password, id FROM user WHERE email = %s"
    cursor.execute(sql, (email,))
    result = cursor.fetchone()

    if result is None or not check_password_hash(result[0], password):
        return jsonify({'error': 'Bad username or password'}), 401

    access_token = create_access_token(identity=result[1])
    return jsonify(access_token=access_token), 200


@app.route('/user', methods=['GET', 'POST'])
@jwt_required
def user():
    if request.method is 'POST':
        data = request.get_json()
        cursor = db.cursor()
        sql = "INSERT INTO user (email, password) VALUES (%s, %s)"
        val = (data['email'], generate_password_hash(data['password']))
        cursor.execute(sql, val)
        db.commit()
        return jsonify({'result': 'ok'}), 200
    else:
        cursor = db.cursor()
        sql = "SELECT id, email FROM user"
        cursor.execute(sql)
        data = cursor.fetchall()

        columns = ['id', 'email']
        result = []
        for k, v1 in enumerate(data):
            row = {}
            for k2, v2 in enumerate(v1):
                row.update({columns[k2]: v2})
            result.append(row)
        return jsonify(result), 200


@app.route('/product', methods=['GET', 'POST'])
@jwt_required
def product():
    print(request.method)
    if request.method == 'POST':
        data = request.get_json()
        cursor = db.cursor()
        sql = "INSERT INTO product (name, brand, image, price) VALUES (%s, %s, %s, %s)"
        val = (data['name'], data['brand'], data['image'], data['price'])
        try:
            cursor.execute(sql, val)
            db.commit()
        except Exception as e:
            print(e)
            return jsonify({'result': 'failed to create. did you sent all the required fields?'}), 500
        return jsonify({'result': 'ok'}), 200
    else:
        cursor = db.cursor()
        sql = "SELECT id, name, brand, image, price FROM product"
        cursor.execute(sql)
        data = cursor.fetchall()

        columns = ['id', 'name', 'brand', 'image', 'price']
        result = []
        for k, v1 in enumerate(data):
            row = {}
            for k2, v2 in enumerate(v1):
                row.update({columns[k2]: v2})
            result.append(row)
        return jsonify(result), 200


@app.route('/cart', methods=['GET'])
@jwt_required
def get_cart():

    cursor = db.cursor()
    sql = "SELECT product.id product_id, name, brand, image, price FROM product, cart_has_product, cart, user WHERE product.id = cart_has_product.product_id AND cart_id = cart.id AND cart.user_id = %s"
    cursor.execute(sql, (get_jwt_identity(), ))
    data = cursor.fetchall()

    columns = ['product_id', 'name', 'brand', 'image', 'price']
    result = []
    for k, v1 in enumerate(data):
        row = {}
        for k2, v2 in enumerate(v1):
            row.update({columns[k2]: v2})
        result.append(row)
    return jsonify(result), 200


@app.route('/cart/<int:cart_id>/product/<int:product_id>', methods=['POST', 'DELETE'])
@jwt_required
def cart(cart_id, product_id):
    if request.method == 'POST':
        try:
            cursor = db.cursor()
            sql = "INSERT INTO cart_has_product (cart_id, product_id) VALUES (%s, %s)"
            val = (cart_id, product_id)
            cursor.execute(sql, val)
            db.commit()
        except Exception as e:
            print(e)
            return jsonify({'result': 'failed to add or remove product to a cart. the cart and the product exists?'}), 500
        return jsonify({'result': 'ok'}), 200

    elif request.method == 'DELETE':
        try:
            cursor = db.cursor()
            sql = "DELETE FROM cart_has_product WHERE cart_id = %s AND product_id = %s"
            val = (cart_id, product_id)
            cursor.execute(sql, val)
            db.commit()
        except Exception as e:
            print(e)
            return jsonify({'result': 'failed to add or remove product to a cart. the cart and the product exists?'}), 500
        return jsonify({'result': 'ok'}), 200
