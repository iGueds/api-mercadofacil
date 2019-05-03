from flask import Flask
import mysql.connector

mydb = mysql.connector.connect(
  host="162.241.2.234",
  user="ghclim06_api",
  passwd="Guedes123",
  database="ghclim06_mercado_facil"
)

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'