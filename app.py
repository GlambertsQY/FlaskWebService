from gensim.models.word2vec import Word2Vec
from flask import Flask, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
import json
import time
import jieba.posseg as jp
import numpy as np
from scipy.linalg import norm
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
model = Word2Vec.load('D:\\Document\\GraduationProject\\Project\\Word2VecTest\\MainPyFile\\wiki_new.model')

app = Flask(__name__)

# 配置flask配置对象中键：SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Abc123456@106.14.141.128/graduationproject?charset=utf8"

# 配置flask配置对象中键：SQLALCHEMY_COMMIT_TEARDOWN,设置为True,应用会自动在每次请求结束后提交数据库中变动
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# 获取SQLAlchemy实例对象，接下来就可以使用对象调用数据
db = SQLAlchemy(app)

flagList = ['n', 'v', 'a', 'd']
sims = [0] * 4
lam = 0
s_len = [0] * 2
alpha1 = 0.8
alpha2 = 0.1
alpha3 = 0.05
alpha4 = 0.05


def sentSimilarity(s1, s2):
    def sentence2Vec(s, n):
        line_cut = jp.cut(s)
        l = []
        dic = {}
        for key in line_cut:
            if key.flag[0] in flagList:
                dic[key.word] = key.flag[0]
                l.append(key.word)
        s_len[n] = len(l)
        v = [np.zeros(64)] * 4
        v_n = [0] * 4
        for key, value in dic.items():
            if value == 'n':
                try:
                    v[0] = v[0] + model[key]
                    v_n[0] = v_n[0] + 1
                except Exception as e:
                    print(e)
            elif value == 'v':
                try:
                    v[1] = v[1] + model[key]
                    v_n[1] = v_n[1] + 1
                except Exception as e:
                    print(e)
            elif value == 'a':
                try:
                    v[2] = v[2] + model[key]
                    v_n[2] = v_n[2] + 1
                except Exception as e:
                    print(e)
            elif value == 'd':
                try:
                    v[3] = v[3] + model[key]
                    v_n[3] = v_n[3] + 1
                except Exception as e:
                    print(e)
            else:
                print('出错')
        for i in range(0, 4):
            if v_n[i] != 0:
                v[i] /= v_n[i]
        return v

    v1, v2 = sentence2Vec(s1, 0), sentence2Vec(s2, 1)
    lam = 2 * min(s_len[0], s_len[1]) / (s_len[0] + s_len[1])
    for i in range(0, 4):
        if any(v1[i]) and any(v2[i]):
            sims[i] = np.dot(v1[i], v2[i]) / (norm(v1[i]) * norm(v2[i]))
    t = lam * (
            alpha1 * sims[0] + alpha2 * sims[1] + alpha3 * sims[2] + alpha4 *
            sims[3])
    if t >= 0.70:
        return 1.0 * 10
    else:
        if t - 0.5 <= 0.0:
            return 0.0
        else:
            return ((t - 0.5) / 0.25) * 10


def sent_most_similarity(s1, s2):
    def sentence2List(s):
        line_cut = jp.cut(s)
        l = []
        for key in line_cut:
            if key.flag[0] == 'n':
                l.append(key.word)
        return l

    l = []
    dic_s = {}
    l1, l2 = sentence2List(s1), sentence2List(s2)
    for i in l1:
        for j in l2:
            try:
                # dic_s[int(model.wv.similarity(i, j) * 100)] = i + ' ' + j
                dic_s[i + ' ' + j] = int(model.wv.similarity(i, j) * 100)
            except Exception as e:
                print(e)
    # dic_s = sorted(dic_s.items(), key=lambda x: x[0], reverse=True)
    for key, value in dic_s.items():
        l.append({'similarity': value, 'ws1': key.split()[0], 'ws2': key.split()[1]})
    return l


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

    # 这个join完的标答提取特别慢
    # standardanswers = db.relationship('StandardAnswer', backref='questions')

    def __repr__(self):
        return '<Question>{}:{}'.format(self.id_q, self.text_q)


class StandardAnswer(db.Model):
    __tablename__ = 'standardanswer'
    id_s = db.Column(db.Integer, primary_key=True, autoincrement='auto')
    text_s = db.Column(db.Text, nullable=False)
    id_q = db.Column(db.Integer, db.ForeignKey(Question.id_q), nullable=False)

    def __repr__(self):
        return '<StandardAnswer>{}:{}'.format(self.id_s, self.text_s)


class Answer(db.Model):
    __tablename__ = 'answer'
    id_a = db.Column(db.Integer, primary_key=True, autoincrement='auto')
    id_q = db.Column(db.Integer, db.ForeignKey(Question.id_q), nullable=False)
    text_a = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Answer>{}:{}'.format(self.id_a, self.text_a)


class Score(db.Model):
    __tablename__ = 'score'
    username = db.Column(db.String(20), db.ForeignKey(User.username), primary_key=True)
    id_a = db.Column(db.Integer, db.ForeignKey(Answer.id_a), primary_key=True)
    time = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Score>{}:{}'.format(self.id_a, self.username)


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
    subject = request.args.get('subject')
    keyword = request.args.get('keyword')
    # if keyword != '':
    question_list = db.session.query(Question, StandardAnswer).filter(Question.id_q == StandardAnswer.id_q,
                                                                      Question.text_q.like(
                                                                          '%' + keyword + '%'),
                                                                      Question.subject == subject).all()
    # else:
    #     question_list = db.session.query(Question).join(StandardAnswer).filter().all()
    #     question_list = db.session.query(Question, StandardAnswer).filter(Question.id_q == StandardAnswer.id_q).all()

    for i in question_list:
        l.append(
            {'id_q': i.Question.id_q, 'title': i.Question.text_q, 'subject': i.Question.subject,
             'standardanswer': i.StandardAnswer.text_s})
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


@app.route('/word_similarity', methods=['POST', 'GET'])
def word_similarity():
    ws1 = ''
    ws2 = ''
    if request.method == 'POST' or request.method == 'GET':
        if request.method == 'POST':
            ws1 = request.form['ws1']
            ws2 = request.form['ws2']
        elif request.method == 'GET':
            ws1 = request.args.get('ws1')
            ws2 = request.args.get('ws2')
        if ws1 == '' or ws2 == '':
            s = {'status': 'invalid parameters'}
            return json.dumps(s, ensure_ascii=False)
        else:
            try:
                sim = str(model.wv.similarity(ws1, ws2))
                s = {'status': 'success', 'ws1': ws1, 'ws2': ws2, 'similarity': sim}
            except Exception as e:
                s = {'status': str(e), 'ws1': ws1, 'ws2': ws2, 'similarity': 0.0}
            finally:
                return json.dumps(s, ensure_ascii=False)
    return "Fail"


@app.route('/sent_similarity', methods=['POST', 'GET'])
def sent_similarity():
    s1 = request.args.get('s1')
    s2 = request.args.get('s2')
    if s1 == '' or s2 == '':
        s = {'status': 'invalid parameters'}
        return json.dumps(s, ensure_ascii=False)
    else:
        similarity = sentSimilarity(s1, s2)
        ll = sent_most_similarity(s1, s2)
        s = {'status': 'success', 'similarity': similarity, 'most_similarity': ll}
        return json.dumps(s, ensure_ascii=False)


# TODO 发信息找回密码和错题报告功能，评分完毕的题目存入题库
@app.route('/getPassword', methods=['POST', 'GET'])
def getPassword():
    username = request.args.get('username')
    try:
        file = open(str(time.strftime('%Y_%m_%d_%H%M%S', time.localtime())) + '_getPassword.txt', 'w', encoding='utf-8')
        file.write(username)
        file.close()
    except Exception as e:
        return 'Fail'
    return 'OK'


@app.route('/sendError', methods=['POST', 'GET'])
def sendError():
    title = request.args.get('title')
    standardanswer = request.args.get('standardanswer')
    answer = request.args.get('answer')
    score = request.args.get('score')
    try:
        file = open(str(time.strftime('%Y_%m_%d_%H%M%S', time.localtime())) + '_sendError.txt', 'w', encoding='utf-8')
        file.write(title + ',' + standardanswer + ',' + answer + ',' + score)
        file.close()
    except Exception as e:
        return 'Fail'
    return 'OK'


@app.route('/store_answer', methods=['POST', 'GET'])
def storeAnswer():
    try:
        id_a = int(db.session.query(Answer).filter().count() + 1)
        id_q = int(request.args.get('id_q'))
        text_a = request.args.get('text_a')
        username = request.args.get('username')
        score = request.args.get('score')
        store_time = str(time.strftime('%Y_%m_%d_%H%M%S', time.localtime()))
        a = Answer(id_a=id_a, id_q=id_q, text_a=text_a)
        s = Score(username=username, id_a=id_a, time=store_time, score=score)
        db.session.add(a)
        db.session.commit()
        db.session.add(s)
        db.session.commit()
    except Exception as e:
        return 'Fail'
    return 'OK'


@app.route('/query_answer', methods=['POST', 'GET'])
def query_answer():
    l = []
    subject = request.args.get('subject')
    keyword = request.args.get('keyword')
    username = request.args.get('username')
    answerList = db.session.query(Answer, Question, Score, StandardAnswer).filter(Question.subject == subject,
                                                                                  Question.text_q.like(
                                                                                      '%' + keyword + '%'
                                                                                  ),
                                                                                  Question.id_q == StandardAnswer.id_q,
                                                                                  Answer.id_q == Question.id_q,
                                                                                  Score.id_a == Answer.id_a,
                                                                                  Score.username == username).all()
    for i in answerList:
        l.append({'id_q': i.Question.id_q, 'id_a': i.Answer.id_a, 'title': i.Question.text_q,
                  'standardanswer': i.StandardAnswer.text_s, 'answer': i.Answer.text_a,
                  'score': i.Score.score, 'score_time': i.Score.time})
    return json.dumps(l, ensure_ascii=False)


if __name__ == '__main__':
    # print(model.wv.similarity('飞机', '火车'))
    db.create_all()
    app.run()
