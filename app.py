from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
import mysql.connector


app = Flask(__name__)

jwt = JWTManager(app)

app.config['JWT_SECRET_KEY'] = "777eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9ovos"
app.config['JWT_HEADER_TYPE'] = ""


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'user' not in data:
        data['user'] = None
    if 'password' not in data:
        data['password'] = None
    user = data['user']
    password = data['password']

    if user == 'aluno' and password == 'impacta':
        return jsonify({'login': True}), 200
    return jsonify({'login': False}), 401

    #cursor = db.cursor(buffered=True)
    #sql = "SELECT password, id FROM user WHERE email = %s"
    #cursor.execute(sql, (email,))
    #result = cursor.fetchone()
    #cursor.close()


    #if result is None or not check_password_hash(result[0], password):
        #return jsonify({'error': 'Bad username or password'}), 401

    #access_token = create_access_token(identity=result[1])
    #return jsonify(access_token=access_token), 200


@app.route('/user', methods=['GET', 'POST'])
#@jwt_required
def user():
    db = mysql.connector.connect(
  host="iguedes.mysql.pythonanywhere-services.com",
  user="iguedes",
  passwd="Ovos12345",
  database="iguedes$mercado_facil"
)
    if request.method is 'POST':
        data = request.get_json()
        cursor = db.cursor(buffered=True)
        sql = "INSERT INTO user (email, password) VALUES (%s, %s)"
        val = (data['email'], generate_password_hash(data['password']))
        cursor.execute(sql, val)
        db.commit()
        cursor.close()

        return jsonify({'result': 'ok'}), 200
    else:

        cursor = db.cursor(buffered=True)
        sql = "SELECT id, email FROM user"
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()

        columns = ['id', 'email']
        result = []
        for k, v1 in enumerate(data):
            row = {}
            for k2, v2 in enumerate(v1):
                row.update({columns[k2]: v2})
            result.append(row)
        return jsonify(result), 200


@app.route('/product', methods=['GET', 'POST'])
#@jwt_required
def product():
    db = mysql.connector.connect(
  host="iguedes.mysql.pythonanywhere-services.com",
  user="iguedes",
  passwd="Ovos12345",
  database="iguedes$mercado_facil"
)
    if request.method == 'POST':
        data = request.get_json()
        cursor = db.cursor(buffered=True)

        if 'image' not in data:
            data['image'] = None

        sql = "INSERT INTO product (name, brand, image, price) VALUES (%s, %s, %s, %s)"
        val = (data['name'], data['brand'], data['image'], data['price'])
        try:
            cursor.execute(sql, val)
            db.commit()
            cursor.close()

        except Exception as e:
            print(e)
            return jsonify({'result': 'failed to create. did you sent all the required fields?'}), 500
        return jsonify({'result': 'ok'}), 200
    else:
        cursor = db.cursor(buffered=True)
        sql = "SELECT id, name, brand, image, price FROM product"
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()

        columns = ['id', 'name', 'brand', 'image', 'price']
        result = []
        for k, v1 in enumerate(data):
            row = {}
            for k2, v2 in enumerate(v1):
                row.update({columns[k2]: v2})
            result.append(row)
        return jsonify(result), 200


@app.route('/cart', methods=['GET'])
#@jwt_required
def get_cart():
    db = mysql.connector.connect(
  host="iguedes.mysql.pythonanywhere-services.com",
  user="iguedes",
  passwd="Ovos12345",
  database="iguedes$mercado_facil"
)
    cursor = db.cursor(buffered=True)
    sql = "SELECT product.id product_id, name, brand, image, price FROM product, cart_has_product, cart, user WHERE product.id = cart_has_product.product_id AND cart_id = cart.id AND cart.user_id = %s"
    cursor.execute(sql, (get_jwt_identity(), ))
    data = cursor.fetchall()
    cursor.close()

    columns = ['product_id', 'name', 'brand', 'image', 'price']
    result = []
    for k, v1 in enumerate(data):
        row = {}
        for k2, v2 in enumerate(v1):
            row.update({columns[k2]: v2})
        result.append(row)
    return jsonify(result), 200


@app.route('/cart/<int:cart_id>/product/<int:product_id>', methods=['POST', 'DELETE'])
#@jwt_required
def cart(cart_id, product_id):
    db = mysql.connector.connect(
  host="iguedes.mysql.pythonanywhere-services.com",
  user="iguedes",
  passwd="Ovos12345",
  database="iguedes$mercado_facil"
)
    if request.method == 'POST':
        try:
            cursor = db.cursor(buffered=True)
            sql = "INSERT INTO cart_has_product (cart_id, product_id) VALUES (%s, %s)"
            val = (cart_id, product_id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()

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
            cursor.close()

        except Exception as e:
            print(e)
            return jsonify({'result': 'failed to add or remove product to a cart. the cart and the product exists?'}), 500
        return jsonify({'result': 'ok'}), 200
