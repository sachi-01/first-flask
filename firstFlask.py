from flask import Flask, render_template, request, redirect, url_for, flash, session
# render_template(.html)跳转到html页面
# request请求函数
# redirect(路由名)即可跳转到路由
# url_for(函数名)即可跳转到函数所在的路由
# flash是闪现
# 因为flask的session是通过加密之后放到了cookie中, 所以有加密就有密钥用于解密
# 所以只要用到了flask的session模块就一定要配置“SECRET_KEY”这个全局宏, 一般设置为24位的字符
from functools import wraps
from flask_bootstrap import Bootstrap
import webbrowser

users = [
    {

        'username': 'root',
        'password': 'root'
    },
]

app = Flask(__name__)
# app.config['SECRER_KEY'] = 'westos'
app.secret_key = 'westos'
# 在接受flash消息时, 需要将消息内容保存在缓存中, 此处是为了进行加密
# 等号后的内容随意, 长度越长加密的越安全
bootstrap = Bootstrap(app)
#导入bootstrap时，实例化对象

def is_login(f):
    """修饰器：用来判断用户是否登录成功"""
    @wraps(f)
    #可以保留被修饰函数的函数名和帮助信息文档
    def wrapper(*args, **kwargs ):
        # 判断session对象中是否有seesion['user']
        # 如果包含信息, 则登录成功, 可以访问主页
        # 如果不包含信息, 则未登录成功, 跳转到登录界面
        if session.get('user', None):
            return f(*args, **kwargs)
        else:
            flash('用户必须登录才能访问%s' %(f.__name__))
            return redirect(url_for('login'))
    return wrapper

def is_admin(f):
    """修饰器：用来判断用户是否登录成功"""
    @wraps(f)
    #可以保留被修饰函数的函数名和帮助信息文档
    def wrapper(*args, **kwargs):
        # 判断session对象中是否有seesion['user']等于root
        # 如果包含信息, 则登录成功, 可以访问主页
        # 如果不包含信息, 则未登录成功, 跳转到登录界面
        if session.get('user', None) == 'root':
            return f(*args, **kwargs)
        else:
            flash('只有管理员root才能访问%s' % (f.__name__))
            return redirect(url_for('login'))
    return wrapper

@app.route('/')
#创建主页路由
def index():
    return render_template('index.html')

@app.route('/register/', methods=['GET', 'POST'])
# 创建注册页面路由, 数据传输方法为GET/POST
def register():
    if request.method == 'POST':
    # 用POST方法保密性更强
        username = request.form.get("username", None)
        password = request.form.get('password', None)
        # 当所有的信息遍历结束, 都没有发现注册的用户存在
        # 则注册成功将注册的新用户信息添加到服务器, 并跳转到登录界面
        for user in users:
            if user['username'] == username:
                return render_template('register.html', message="用户%s已经存在" % (username))
        else:
            users.append(dict(username=username, password=password))
            # 出现一个闪现信息;
            flash("用户%s已经注册成功， 请登录....." % (username), category='info')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login/', methods=['GET', 'POST'])
#创建登录页面路由，数据传输方法为GET/POST
def login():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        for user in users:
            if user['username'] == username and user['password'] == password:
                #将用户登录的信息存储到session中
                session['user'] = username
                return redirect(url_for('index'))
        else:
            #出现一个闪现消息
            flash('用户%s密码错误， 请重新登录 ......' % (username))
            return  redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout/')
#创建用户注销登录路由
def logout():
    #将用户储存到session中的信息删除
    session.pop('user')
    flash('注销成功......')
    return redirect(url_for('login'))

@app.route('/delete/<string:username>/')
# 创建删除用户路由
def delete(username):
    for user in users:
        # 用户存在, 则删除
        if username == user['username']:
            users.remove(user)
            flash("删除用户%s成功" % (username))

@app.route('/list/')
#创建查看用户信息路由
@is_login
@is_admin
def list():
    return render_template('list.html', users=users)

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000/')
    app.run()

