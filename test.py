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

file_list = os.listdir("./data")

count = 0  
book = []
for file in file_list:
    book_temp = book_dt()
    with open('data/'+file) as f:
        reader = csv.reader(f)
        for row in reader:
            if(row[0] == 'title'):
                print(row[1])
                book_temp.title = row[1]
            if(row[0] == 'img'):
                book_temp.img = row[1]
            if(row[0] == 'review'):
                review_temp = review_dt()
                review_temp.rank = row[1]
                review_temp.name = row[2]
                review_temp.text = row[3]
                book_temp.review.append(review_temp)
                print("☆" + review_temp.rank + review_temp.name +"さん曰く、"+ review_temp.text)
            if(row[0] == 'lend'):
                if (row[1] == '1'):
                    print("貸し出し中")
                else:
                    print("いける")
    book.append( book_temp)
print(book)  

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
