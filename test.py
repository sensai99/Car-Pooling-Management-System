from authy.api import AuthyApiClient
from flask import Flask, render_template, redirect, session, url_for, request, Response
from flask_mysqldb import MySQL
import MySQLdb

app = Flask(__name__)

# for default page
@app.route('/')
def home():
    return render_template("test.html")


if __name__ == '__main__':
    app.run(debug = False)