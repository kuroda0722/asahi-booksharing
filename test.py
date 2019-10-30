# coding: utf-8


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
    with open('./data/'+file, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if(row[0] == 'title'):
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
    book.append(book_temp)
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
@app.route('/home')
def home():
    """Renders the home page."""
    str = ''
    cur.execute("SELECT title,img_url FROM book;")
    for i in range(20):
        data = cur.fetchone()
        if data is None:
            break
        else:
            str += ('<a href="/book/{0}"><img src = "{1}" width="300"></a>').format(data[0],data[1])
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        message=str
    )

@app.route('/book')
@app.route('/book/<title>')
def bookpage(title = ''):
    cur.execute(("SELECT * FROM book where title = '{0}';").format(title))
    data = cur.fetchone()
    return render_template(
        'book.html',
        year=datetime.now().year,
        title=data[1],
        review = "test",
        lend = data[6]
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