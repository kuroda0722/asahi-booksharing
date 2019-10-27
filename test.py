# coding: utf-8


from datetime import datetime
from flask import Flask, request, Response, abort, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from collections import defaultdict
import csv
import os

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
    with open('./data/'+file) as f:
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
    for b in book:
        str+='<a href="./book/'+b.title+'">'
        str+=('<img src = "./data/' + b.img + '">')
        str+=b.title
        str+='</a>   '
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        message=str
    )

@app.route('/book')
@app.route('/book/<title>')
def bookpage(title = ''):
    print(title)
    b = 0
    for bb in book:
        if bb.title == title:
            b = bb
    lend_str=''
    if b.lend:
        lend_str='貸し出し中です。'
    else:
        lend_str='貸し出し可能です。'
    review_str = ''
    for r in b.review:
        review_str +=(r.name + r.rank + r.text)
        review_str += '</br>'
    
    return render_template(
        'book.html',
        year=datetime.now().year,
        title=b.title,
        review = review_str,
        lend = lend_str
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
@app.route('/protected/')
@login_required
def protected():
    return Response('''
    protected<br />
    <a href="/logout/">logout</a>
    ''')

# ログインパス
@app.route('/login/', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        # ユーザーチェック
        if(request.form["username"] in user_check and request.form["password"] == user_check[request.form["username"]]["password"]):
            # ユーザーが存在した場合はログイン
            login_user(users.get(user_check[request.form["username"]]["id"]))
            return Response('''
            ogin success!<br />
            #<a href="/protected/">protected</a><br />
            <a href="/logout/">logout</a>
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
    
    return Response('''
    logout success!<br />
    <a href="/login/">login</a>
    ''')

#@app.route('/')
#def index():
#    return "Hello World !"  

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
