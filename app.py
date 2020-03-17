from gensim.models.word2vec import Word2Vec
from flask import Flask, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
import json
import time

app = Flask(__name__)

# model = Word2Vec.load('D:\\Document\\GraduationProject\\Project\\Word2VecTest\\Test\\wiki_new.model')

# 配置flask配置对象中键：SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Abc123456@106.14.141.128/graduationproject?charset=utf8"

# 配置flask配置对象中键：SQLALCHEMY_COMMIT_TEARDOWN,设置为True,应用会自动在每次请求结束后提交数据库中变动
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# 获取SQLAlchemy实例对象，接下来就可以使用对象调用数据
db = SQLAlchemy(app)


# 创建模型对象
class User(db.Model):
    __tablename__ = "user"
    username = db.Column(db.String(20), nullable=False, primary_key=True)
    password = db.Column(db.String(20), nullable=False)
    mail = db.Column(db.String(30), nullable=True)
    phone = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return '<User %r>' % self.username


class Question(db.Model):  # 必须继承declaraive_base得到的那个基类
    __tablename__ = "question"  # 必须要有__tablename__来指出这个类对应什么表，这个表可以暂时在库中不存在，SQLAlchemy会帮我们创建这个表
    id_q = db.Column(db.Integer, primary_key=True, autoincrement='auto')  # Column类创建一个字段
    text_q = db.Column(db.Text,
                       nullable=False)  # nullable就是决定是否not null，unique就是决定是否unique。。这里假定没人重名，设置index可以让系统自动根据这个字段为基础建立索引
    subject = db.Column(db.String(20), nullable=False)

    standardanswers = db.relationship('StandardAnswer', backref='questions')

    def __repr__(self):
        return '<Question>{}:{}'.format(self.id_q, self.text_q)


class StandardAnswer(db.Model):
    __tablename__ = 'standardanswer'
    id_s = db.Column(db.Integer, primary_key=True, autoincrement='auto')
    text_s = db.Column(db.Text, nullable=False)
    id_q = db.Column(db.Integer, db.ForeignKey(Question.id_q), nullable=False)

    def __repr__(self):
        return '<StandardAnswer>{}:{}'.format(self.id_s, self.text_s)


@app.route('/questionlist')
def question_list():
    l = []
    question_list = db.session.query(Question).filter().all()
    for i in question_list:
        l.append({'id_q': i.id_q, 'text': i.text_q, 'subject': i.subject})
    return json.dumps(l, ensure_ascii=False)


@app.route('/questionstandardanswerlist', methods=['POST', 'GET'])
def question_search():
    l = []
    sTime = time.time()
    keyword = request.args.get('keyword')
    if keyword != '':
        question_list = db.session.query(Question).join(StandardAnswer).filter(
            Question.text_q.like('%' + keyword + '%')).all()
    else:
        question_list = db.session.query(Question).join(StandardAnswer).filter().all()

    for i in question_list:
        l.append(
            {'id_q': i.id_q, 'title': i.text_q, 'subject': i.subject, 'standardanswer': i.standardanswers[0].text_s})

    eTime = time.time()
    print('耗时：' + str(int((eTime - sTime) * 1000)) + 'ms')
    return json.dumps(l, ensure_ascii=False)


@app.route('/standardanswerlist')
def standardanswer_list():
    l = []
    standardanswer_list = db.session.query(StandardAnswer).filter().all()
    for i in standardanswer_list:
        l.append({'id_s': i.id_s, 'text': i.text_s, 'id_q': i.id_q})
    return json.dumps(l, ensure_ascii=False)


@app.route('/add_questionStandardAnswer', methods=['POST', 'GET'])
def add_questionStandardAnswer():
    try:
        id_q = int(db.session.query(Question).filter().count() + 1)
        id_s = id_q
        sub = request.args.get('subject')
        text_q = request.args.get('title')
        text_s = subject = request.args.get('standardanswer')
        q = Question(id_q=id_q, text_q=text_q, subject=sub)
        s = StandardAnswer(id_s=id_s, text_s=text_s, id_q=id_q)
        db.session.add(q)
        db.session.add(s)
        db.session.commit()
    except Exception as e:
        return "Fail"
    return "OK"


@app.route('/userList')
def user_list():
    # user_list = User.query.all()
    user_list = User.query.order_by(User.id).all()
    return str(user_list[0].user_name)


@app.route('/queryUser', methods=['POST', 'GET'])
def query_user():
    username = request.args.get('username')
    password = request.args.get('password')
    user_list = db.session.query(User).filter(User.username == username, User.password == password).all()
    if len(user_list) != 0:
        return "OK"
    else:
        return "Fail"


@app.route('/query_userByName', methods=['POST', 'GET'])
def query_userByName():
    l = {}
    username = request.args.get('username')
    user_list = db.session.query(User).filter(User.username == username).all()
    for u in user_list:
        l = {'username': u.username, 'password': u.password, 'phone': u.phone
            , 'mail': u.mail}
    return json.dumps(l, ensure_ascii=False)


@app.route('/add_user', methods=['POST', 'GET'])
def user_add():
    try:
        username = request.args.get('username')
        password = request.args.get('password')
        phone = request.args.get('phone')
        mail = request.args.get('mail')
        u = User(username=username, password=password, phone=phone, mail=mail)
        db.session.add(u)
        db.session.commit()
    except Exception as e:
        return "Fail"
    return "OK"


@app.route('/update_user', methods=['POST', 'GET'])
def user_update():
    try:
        old_username = request.args.get('old_username')
        new_username = request.args.get('new_username')
        password = request.args.get('password')
        phone = request.args.get('phone')
        mail = request.args.get('mail')
        db.session.query(User).filter(User.username == old_username).update(
            {"username": new_username, "password": password, "phone": phone, "mail": mail})
        db.session.commit()
    except Exception as e:
        return "Fail"
    return "OK"


@app.route('/user_delete')
def user_delete():
    user = User.query.filter_by(id=1).first()
    db.session.delete(user)
    db.session.commit()

    return "OK"


@app.route('/')
def hello_world():
    return 'https://sub2.ivy.best/osubscribe.php?sid=742&token=oG9t0jNIlBzt'


# @app.route('/similarity', methods=['POST', 'GET'])
# def similarity():
#     ws1 = ''
#     ws2 = ''
#     if request.method == 'POST' or request.method == 'GET':
#         if request.method == 'POST':
#             ws1 = request.form['ws1']
#             ws2 = request.form['ws2']
#         elif request.method == 'GET':
#             ws1 = request.args.get('ws1')
#             ws2 = request.args.get('ws2')
#         if ws1 == '' or ws2 == '':
#             s = {'status': 'invalid parameters'}
#             return json.dumps(s, ensure_ascii=False)
#         else:
#             try:
#                 sim = str(model.wv.similarity(ws1, ws2))
#                 s = {'status': 'success', 'ws1': ws1, 'ws2': ws2, 'similarity': sim}
#             except Exception as e:
#                 s = {'status': str(e), 'ws1': ws1, 'ws2': ws2, 'similarity': 0.0}
#             finally:
#                 return json.dumps(s, ensure_ascii=False)
#     title = request.args.get('title', 'Default')
#     return render_template('similarity.html', title=title)


if __name__ == '__main__':
    # print(model.wv.similarity('飞机', '火车'))
    db.create_all()
    app.run()
