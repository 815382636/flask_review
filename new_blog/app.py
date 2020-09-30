from flask import Flask, render_template, url_for, redirect, request, session
from models import User, Question, Comment
from exts import db
import config
from decorators import login_required

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
def index():
    a = 1
    content = {
        'questions': Question.query.order_by(Question.create_time.desc()).all()
    }
    return render_template('index.html', **content)


@app.route('/comment/', methods=['POST'])
@login_required
def comment():
    content =request.form.get('content')
    question_id =request.form.get("question_id")
    comment =Comment(content=content)
    user_id =session.get("user_id")
    user=User.query.filter(User.id ==user_id).first()
    comment.author =user
    question =Question.query.filter(Question.id ==question_id).first()
    comment.question =question
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('detail',question_id=question_id))

@app.route('/detail/<question_id>')
def detail(question_id):
    question = Question.query.filter(Question.id == question_id).first()
    return render_template('detail.html', question=question)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone, User.password == password).first()
        if user:
            session['user_id'] = user.id
            # 如果31天自动登录
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return '手机号码或密码错误'


@app.route('/regist/', methods=['GET', 'POST'])
def regist():
    if request.method == "GET":
        return render_template('regist.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return '该手机号码已被注册'
        else:
            if password1 != password2:
                return '两次密码不相等'
            else:
                user = User(telephone=telephone, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))


@app.route('/logout/')
def logout():
    session.pop('user_id')
    # session.clear()
    return redirect(url_for('login'))


@app.route('/question/', methods=['GET', 'POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get("title")
        content = request.form.get("content")
        question = Question(title=title, content=content)
        user = User.query.filter(User.id == session.get("user_id")).first()
        question.author = user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))


# 被这个装饰器修饰的钩子函数，必须返回一个字典，即使是空字典
@app.context_processor
def my_context_processor():
    user_id = session.get("user_id")
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user': user}
    return {}


# url_for(def_name)-->url  反转
# redirect（url）            重定向

if __name__ == '__main__':
    app.run()
