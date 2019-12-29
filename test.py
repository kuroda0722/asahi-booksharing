# coding: utf-8
from datetime import datetime
from flask import Flask, request, Response, abort, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from collections import defaultdict
import csv
import os
import psycopg2
import random
import requests

conn = psycopg2.connect(\
    host='ec2-54-235-92-43.compute-1.amazonaws.com',\
    user='yukvwzgkmgumwn',\
    password='2127634225d512ead95dff681a0b804f8f5a3a468017c734f80d72d3dd84f722',\
    database='d3tspi511bpse4',\
    port=5432) 
cur = conn.cursor()

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


class reserver_dt():
    def __init__(self,data = None):
        if data is None:
            self.number = 0
            self.name = ''
            self.time = ''
        else:
            self.number = data[0]
            self.name = data[1]
            self.time = data[2]

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


def convert_newline(str):
    i = str.find('\r')
    if i == -1:
        return str
    str2 = ''
    if i > 0:
        str2 += str[:i]
    str2 += '<br>'
    if i+1 < len(str):
        str2 += str[i+2:]
    print (i,str2)
    return str2

@app.route('/', methods=["GET", "POST"])
@app.route('/home', methods=["GET", "POST"])
def home():
    """Renders the home page."""
    str = ''
    b_list = []
    cur.execute("SELECT * FROM book ORDER BY time;")
    for i in range(99):
        data = cur.fetchone()
        if data is None:
            break
        else:
            b = book_dt(data)
            b_list.append(b)
            str += ('<div class="col-md-3 col-sm-4 col-xs-6 "><div ><a href="/book/{0}"><img src = "{1}" class="img-responsive" style="width: 300px; height: 420px;object-fit: contain;"></a></div></div>').format(b.title,b.img_url)
    if(request.method == "POST"):
        print(len(b_list))
        n = len(b_list)
        r = random.uniform(0, n-1)
        return  Response('''
                    <meta http-equiv="Refresh" content="0;URL=/book/{0}">
                    '''.format(b_list[int(r)].title))
    else:
        return render_template(
            'index.html',
            title='Home Page',
            year=datetime.now().year,
            message=str
        )

@app.route('/book', methods=["GET", "POST"])
@app.route('/book/<title>', methods=["GET", "POST"])
@app.route('/book/<title>/<command>/<val>', methods=["GET", "POST"])
def bookpage(title = '',command = '',val=''):
    cur.execute(("SELECT * FROM book where title = '{0}';").format(title))
    data = cur.fetchone()
    b = book_dt(data)

    if command == 'cancel':
        if(request.method == "GET"):
            return  Response('''
                予約をキャンセルしますか？<br>
                <form method="post"><button value="yes" name="name">はい</button><button value="no" name="name">いいえ</button></form>
                '''.format(title))
        else:
            flag = request.form["name"]
            if (flag == 'yes'):
                s = ("DELETE FROM reserver{0} where number = {1};").format(b.number,val)
                print (s)
                cur.execute(s)
                conn.commit()
                return  Response('''
                <meta http-equiv="Refresh" content="0;URL=../book/{0}">
                '''.format(b.title))
            else:
                return  Response('''
                <meta http-equiv="Refresh" content="0;URL=../book/{0}">
                '''.format(b.title))

    if command == 'delete':
        if(request.method == "GET"):
            return  Response('''
                削除してよろしいですか？<br>
                <form method="post"><button value="yes" name="name">はい</button><button value="no" name="name">いいえ</button></form>
                '''.format(title))
        else:
            flag = request.form["name"]
            if (flag == 'yes'):
                s = ("DELETE FROM review{0} where number = {1};").format(b.number,val)
                print (s)
                cur.execute(s)
                conn.commit()
                return  Response('''
                <meta http-equiv="Refresh" content="0;URL=../book/{0}">
                '''.format(b.title))
            else:
                return  Response('''
                <meta http-equiv="Refresh" content="0;URL=../book/{0}">
                '''.format(b.title))

    #show reserver
    cur.execute(("SELECT * FROM information_schema.tables WHERE table_name = 'reserver{0}';").format(b.number))
    data = cur.fetchone()
    if data is None:
        str = '''
            CREATE TABLE reserver{0}(
            number int,
            name varchar(32),
            time timestamp
            );
        '''.format(b.number)
        cur.execute(str)
        conn.commit()
    cur.execute(("SELECT * FROM reserver{0} ORDER BY time;").format(b.number))
    reserver_str=''
    reserver_num = 0
    for i in range(99):
        data = cur.fetchone()
        if data is None:
            if reserver_num == 0:
                b.lend = False
            break
        else:
            b.lend = True
            r = reserver_dt(data)
            reserver_num+=1
            reserver_str += '<p>{0}  '.format(r.name)
            reserver_str += '<a href = "/book/{0}/cancel/{1}"><button type="submit" class="btn-xs">キャンセル</button></a></p>'.format(b.title,r.number)
    if b.lend:
        reserver_str = '<h4>貸し出し中です。</h4><h5>予約者一覧</h5>' + reserver_str
    else:
        reserver_str = '<h4>貸し出し可能です。</h4>'
    
    cur.execute(("UPDATE book SET lend = {0} WHERE number = {1};").format(int(b.lend),b.number))
    conn.commit()

    #show review
    cur.execute(("SELECT * FROM information_schema.tables WHERE table_name = 'review{0}';").format(b.number))
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
            review_str += """<div class = "col panel pannel-default">"""
            #review_str+=('<p><span class="lead">{0} ').format(r.title)
            review_str+='<font color = "#ffa500">'
            for j in range(5):
                if j < r.rank:
                    review_str += "★"
                else:
                    review_str += "☆"
            review_str+='</font></span> '
            review_str+=(' by {0}  {1}  ').format(r.name,r.time)
            review_str+= '<a href = "/book/{0}/delete/{1}"><button type="submit" class="btn-xs">削除</button></a></p>'.format(b.title,r.number)
            review_str+=('<p>{0}</p>').format(r.text)
            review_str += '</div>'
    new_review = review_dt()
    rev = ['selected',0,0,0,0,0]
    input_error = ''
    reserve_input_error = ''
    if(request.method == "POST"):
        if request.form["action"] == 'submit_reserve':
            reserver_name = request.form["reserver_name"]
            if(reserver_name == ''):
                reserve_input_error = '<div class="alert alert-danger" role="alert">名前を入力してください。</div>'
            else:
                #予約実行
                cur.execute("SELECT MAX(number) FROM reserver{0};".format(b.number))
                data = cur.fetchone()
                num = 0
                if data[0] is not None:
                        num = int(data[0])+1
                print(reserver_name)
                s = ("""INSERT INTO reserver{0} VALUES ({1}, '{2}', '{3}');""").format(b.number,num,reserver_name,"{0:%Y/%m/%d %H:%M:%S}".format(datetime.now()),new_review.title)
                print(s)
                cur.execute(s)
                conn.commit()
                """
                line_notify_token = os.environ["LINE_TOKEN"]
                line_notify_api = 'https://notify-api.line.me/api/notify'
                line_message = '{0} {1} 予約しました'.format(b.number,num,reserver_name)


                payload = {'message': line_message}
                headers = {'Authorization': 'Bearer ' + line_notify_token}  # 発行したトークン
                line_notify = requests.post(line_notify_api, data=payload, headers=headers)
                """
                return  Response('''
                    <meta http-equiv="Refresh" content="0;URL=/book/{0}">
                    '''.format(b.title))
        else:
            new_review.name = request.form["name"]        
            new_review.rank = request.form["rank"]        
            new_review.title = 'notitle'#request.form["title"]        
            new_review.text = request.form["main"]
            while True:
                temp = new_review.text
                new_review.text = convert_newline(new_review.text)
                if temp == new_review.text:
                    break

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
                cur.execute("SELECT MAX(number) FROM review{0};".format(b.number))
                data = cur.fetchone()
                num = 0
                if data[0] is not None:
                     num = int(data[0])+1
                s = ("""INSERT INTO review{0} VALUES ({1}, {2}, '{3}','{4}','{5}','{6}');""").format(b.number,num,new_review.rank,new_review.name,new_review.text,"{0:%Y/%m/%d %H:%M:%S}".format(datetime.now()),new_review.title)
                print(s)
                cur.execute(s)
                conn.commit()
                return  Response('''
                <meta http-equiv="Refresh" content="0;URL=/book/{0}">
                '''.format(b.title))
    
    return render_template(
        'book.html',
        year=datetime.now().year,
        title=b.title,
        img=b.img_url,
        review_num=review_num,
        review_main = review_str,
        lend = reserver_str,
        re_name = new_review.name, re_title = new_review.title, re_text = new_review.text,
        re_rank0 = rev[0],re_rank1 = rev[1],re_rank2 = rev[2],re_rank3 = rev[3],re_rank4 = rev[4],re_rank5 = rev[5],
        input_error = input_error,
        reserve_input_error = reserve_input_error
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

@app.route('/rule')
def rule():
    """Renders the about page."""
    return render_template(
        'rule.html',
        title='ルール'
    )

# ログインしないと表示されないパス
@app.route('/add_book/', methods=["GET", "POST"])
@login_required
def protected():
    str = ''
    book_list = []
    cur.execute("SELECT * FROM book ORDER BY time;")
    for i in range(99):
        data = cur.fetchone()
        if data is None:
            break
        else:
            b = book_dt(data)
            book_list.append(b)
            str += ('<div class="col-md-3 col-sm-4 col-xs-6 "><div ><a href="/delete_book/{0}"><img src = "{1}" class="img-responsive" style="width: 300px; height: 420px;object-fit: contain;"></a></div></div>').format(b.title,b.img_url)
    str_reserver_list = ''
    for b in book_list:
        cur.execute(("SELECT * FROM information_schema.tables WHERE table_name = 'reserver{0}';").format(b.number))
        data = cur.fetchone()
        if data is None:
            str_reserver_list += '予約者なし'
        else:
            cur.execute("SELECT * FROM reserver{0} ORDER BY time;".format(b.number))
            str_reserver_list += '<h4>' + b.title + '</h4>'
            for i in range(99):
                data = cur.fetchone()
                if data is None:
                    if i == 0:
                        str_reserver_list += '予約者なし'
                    break
                else:
                    r = reserver_dt(data)
                    str_reserver_list += '<p>' + r.name + '  '+ "{0:%Y/%m/%d %H:%M:%S}".format(r.time) + '</p>'
    if(request.method == "POST"):
        cur.execute("SELECT MAX(number) FROM book;")
        data = cur.fetchone()
        num = data[0]+1

        title = request.form["name"]
        img_url = request.form["image"]
        s = ("""INSERT INTO book VALUES ({0}, '{1}', '{2}',{3},'{4}','{5}',{6},'{7}');""").format(num,title,img_url,1,"a","a",0,"{0:%Y/%m/%d %H:%M:%S}".format(datetime.now()))
        print(s)
        cur.execute(s)
        conn.commit()
        return  Response('''
        <meta http-equiv="Refresh" content="0;URL=/home">
        ''')
    else:
        return render_template('add_book.html',message=str,reserver_list=str_reserver_list)

@login_required
@app.route('/delete_book/<title>', methods=["GET", "POST"])
def delete_book(title):
    cur.execute(("SELECT * FROM book where title = '{0}';").format(title))
    data = cur.fetchone()
    b = book_dt(data)
    if(request.method == "GET"):
        return  Response('''
            本を削除しますか？<br>
            <form method="post"><button value="yes" name="name">はい</button><button value="no" name="name">いいえ</button></form>
            '''.format(title))
    else:
        flag = request.form["name"]
        if flag == 'yes':
            cur.execute("DELETE FROM book where number = {0};".format(b.number))
            conn.commit()

            cur.execute(("SELECT * FROM information_schema.tables WHERE table_name = 'review{0}';").format(b.number))
            data = cur.fetchone()
            if not data is None:
                cur.execute("DROP TABLE review{0};".format(b.number))
                conn.commit()

            cur.execute(("SELECT * FROM information_schema.tables WHERE table_name = 'reserver{0}';").format(b.number))
            data = cur.fetchone()
            if not data is None:
                cur.execute("DROP TABLE reserver{0};".format(b.number))
                conn.commit()
            return  Response('''
                <meta http-equiv="Refresh" content="0;URL=../">
                ''')
        else:
            return  Response('''
                <meta http-equiv="Refresh" content="0;URL=../">
                ''')

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