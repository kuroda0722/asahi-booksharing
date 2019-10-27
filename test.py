# coding: utf-8


from datetime import datetime
from flask import Flask, request, Response, abort, render_template
import csv
import os

app = Flask(__name__)

class review_dt:
    def __init__(self):
        self.rank = 0
        self.name = ''
        self.text = ''
        self.date = ''

class chat_dt:
    def __init__(self):
        self.name = ''
        self.text = ''
        self.date = ''

class book_dt:
    def __init__(self):
        self.title = ''
        self.img = ''
        self.level = 0
        self.review = []
        self.chat = chat_dt()
        self.lend = False
        self.reserver = ''
        self.date = ''

     

@app.route('/')
def index():
    return "Hello World !"  

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
