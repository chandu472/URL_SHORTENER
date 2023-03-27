import os
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import validators
import random
import string
import hashlib
from datetime import datetime

app = Flask(__name__)

########SQL ALCHEMY CONFIGURATION###############

basedir = os.path.abspath(os.path.dirname(__file__))
path = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

#########CREATE MODEL###########################

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False, unique=True)
    short_url = db.Column(db.String(10), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Url('{self.original_url}', '{self.short_url}', '{self.created_at}')"


@app.before_first_request
def create_tables():
    db.create_all()

def shorten_url(url):
    """Generate a shortened URL from the given URL"""
    hash_object = hashlib.sha1(url.encode())
    hex_dig = hash_object.hexdigest()
    short_hex_dig = hex_dig[:7] # Use first 7 characters of the hash as the shortened URL
    return short_hex_dig

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form.get('original-url')
        if not original_url.startswith('http'):
            original_url = 'http://' + original_url
        short_url = shorten_url(original_url)
        new_url = Url(original_url=original_url, short_url=short_url)
        db.session.add(new_url)
        db.session.commit()
        return render_template('result.html', short_url=short_url)
    return render_template('home.html')

@app.route('/<short_url>')
def redirect_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first_or_404()
    return redirect(url.original_url)

@app.route('/history')
def history():
    urls = Url.query.order_by(Url.created_at.desc()).all()
    return render_template('history.html', urls=urls)

if __name__ == '__main__':
    app.run(debug=True)

