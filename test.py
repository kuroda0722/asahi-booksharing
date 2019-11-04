﻿# coding: utf-8
from datetime import datetime
from flask import Flask, request, Response, abort, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from collections import defaultdict
import csv
import os
import psycopg2

conn = psycopg2.connect(\
    host='ec2-54-235-92-43.compute-1.amazonaws.com',\
    user='yukvwzgkmgumwn',\
    password='2127634225d512ead95dff681a0b804f8f5a3a468017c734f80d72d3dd84f722',\
    database='d3tspi511bpse4',\
    port=5432) 
cur = conn.cursor()
cur.execute("SELECT * FROM sample;")
results = cur.fetchone()
print(results)
results = cur.fetchone()
print(results)
conn.commit()

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = "secret"

class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

# ログイン用ユーザー作成
users = {
    1: User(1, "numata", "kuroda"),
    2: User(2, "kuroda", "numata"),
}
@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

# ユーザーチェックに使用する辞書作成
nested_dict = lambda: defaultdict(nested_dict)
user_check = nested_dict()
for i in users.values():
    user_check[i.name]["password"] = i.password
    user_check[i.name]["id"] = i.id


class review_dt:
    def __init__(self,data = None):
        if data is None:
            self.number = 0
            self.rank = 0
            self.name = ''
            self.text = ''
            self.time = ''
            self.title = ''
        else:
            self.number = data[0]
            self.name = data[2]
            self.rank = data[1]
            self.text = data[3]
            self.time= data[4]
            self.title = data[5]

class chat_dt:
    def __init__(self):
        self.name = ''
        self.text = ''
        self.date = ''

class book_dt:
    def __init__(self):
        self.number = 0
        self.title = ''
        self.img_url = ''
        self.level = 0
        self.review = ''
        self.chat = ''
        self.lend = False
        self.reserver = ''
        self.time  = ''
    def __init__(self,data):
        self.number = data[0]
        self.title = data[1]
        self.img_url = data[2]
        self.level= data[3]
        self.review= data[4]
        self.chat= data[5]
        self.lend= data[6]
        self.time = data[7]

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    str = ''
    cur.execute("SELECT * FROM book;")
    for i in range(99):
        data = cur.fetchone()
        if data is None:
            break
        else:
            b = book_dt(data)
            str += ('<div class="col-md-3 col-sm-4 col-xs-6 "><a href="/book/{0}"><h4>{0}</h4><p><img src = "{1}" class="img-responsive"></p></a></div>').format(b.title,b.img_url)
          
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        message=str
    )

@app.route('/book', methods=["GET", "POST"])
@app.route('/book/<title>', methods=["GET", "POST"])
def bookpage(title = ''):
    cur.execute(("SELECT * FROM book where title = '{0}';").format(title))
    data = cur.fetchone()
    b = book_dt(data)
    cur.execute(("SELECT * FROM information_schema.tables WHERE table_name = 'review{}';").format(b.number))
    data = cur.fetchone()
    if data is None:
        str = '''
            CREATE TABLE review{0}(
            number int,
            rank int,
            name varchar(32),
            text varchar(1024),
            time timestamp,
            title varchar(64)
            );
        '''.format(b.number)
        cur.execute(str)
        conn.commit()
    cur.execute(("SELECT * FROM review{0} ORDER BY time DESC;").format(b.number))
    review_str=''
    review_num = 0
    for i in range(99):
        data = cur.fetchone()
        if data is None:
            if review_num == 0:
                review_str+='本のレビューはありません。'
            break
        else:
            r = review_dt(data)
        
            review_num += 1
            review_str+=('<h4>{0} ☆{2}</h4><p>by {1} - {4}</p><p>{3}</p>').format(r.title,r.name,r.rank,r.text,r.time)
    
    new_review = review_dt()
    rev = ['selected',0,0,0,0,0]
    input_error = ''
    if(request.method == "POST"):
        new_review.name = request.form["name"]        
        new_review.rank = request.form["rank"]        
        new_review.title = request.form["title"]        
        new_review.text = request.form["main"]

        if new_review.rank == 'rank5':
            rev[5] = 'selected'
            new_review.rank = 5
        elif new_review.rank == 'rank1':
            rev[1] = 'selected'
            new_review.rank = 1
        elif new_review.rank == 'rank2':
            rev[2] = 'selected'
            new_review.rank = 2
        elif new_review.rank == 'rank3':
            rev[3] = 'selected'
            new_review.rank = 3
        elif new_review.rank == 'rank4':
            rev[4] = 'selected'
            new_review.rank = 4
        else:
            rev[0] = 'selected'
            new_review.rank = 0

        if(new_review.name == '' or new_review.rank == 0 or  new_review.title == '' or new_review.text == ''):
            input_error = '<div class="alert alert-danger" role="alert">入力エラーです。</div>'
        else:
            cur.execute("SELECT MAX(number) FROM book;")
            data = cur.fetchone()
            num = data[0]+1
            s = ("INSERT INTO review{0} VALUES ({1}, {2}, '{3}','{4}','{5}','{6}');").format(b.number,num,new_review.rank,new_review.name,new_review.text,datetime.now(),new_review.title)
            print(s)
            cur.execute(s)
            conn.commit()
            return  Response('''
            <meta http-equiv="Refresh" content="0;URL=../book/{0}">
            '''.format(b.title))
    
    return render_template(
        'book.html',
        year=datetime.now().year,
        title=b.title,
        img=b.img_url,
        review_num=review_num,
        review_main = review_str,
        lend = "貸し出し中です。" if b.lend else "貸し出し可能です。",
        re_name = new_review.name, re_title = new_review.title, re_text = new_review.text,
        re_rank0 = rev[0],re_rank1 = rev[1],re_rank2 = rev[2],re_rank3 = rev[3],re_rank4 = rev[4],re_rank5 = rev[5],
        input_error = input_error
    )    

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

# ログインしないと表示されないパス
@app.route('/add_book/', methods=["GET", "POST"])
@login_required
def protected():
    if(request.method == "POST"):
        cur.execute("SELECT MAX(number) FROM book;")
        data = cur.fetchone()
        num = data[0]+1

        title = request.form["name"]
        img_url = request.form["image"]
        s = ("INSERT INTO book VALUES ({0}, '{1}', '{2}',{3},'{4}','{5}',{6},'{7}');").format(num,title,img_url,1,"a","a",0,datetime.now())
        print(s)
        cur.execute(s)
        conn.commit()
        return render_template('add_book.html')
    else:
        return render_template('add_book.html')

# ログインパス
@app.route('/login/', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        # ユーザーチェック
        if(request.form["username"] in user_check and request.form["password"] == user_check[request.form["username"]]["password"]):
            # ユーザーが存在した場合はログイン
            login_user(users.get(user_check[request.form["username"]]["id"]))
            return  Response('''
            <meta http-equiv="Refresh" content="0;URL=../add_book">
            ''')
        else:
            return abort(401)
    else:
        return render_template("login.html")

# ログアウトパス
@app.route('/logout/')
#@login_required
def logout():
    logout_user()
    return  Response('''
        <meta http-equiv="Refresh" content="0;URL=/home">
    ''')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')


#cur.close()
#conn.close()