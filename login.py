from flask import Flask,render_template,request,redirect
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
import pymysql
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func



app = Flask(__name__)
#首先链接数据库库名Users
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123456@127.0.0.1/hospital"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#指定为调试模式
app.config['DEBUG'] = True
#制定执行完增删改查之后的自动提交
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
#创建SQLALchemy的实例
db= SQLAlchemy(app)
# 创建Manager对象并制定要挂不努力的app
manager = Manager(app)

# 创建Migrate的对象，并制定关联的app和db

migrate = Migrate(app,db)

#为manager增加数据库的迁移指令
# 为manager 增加一个自命令-db，具体操作由MigrateCommand
manager.add_command('db',MigrateCommand)
class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(32),nullable = False,index = True)
    userpwd = db.Column(db.String(100),nullable = False)
    # 工作岗位
    jop = db.Column(db.String(100),nullable = False,index = True)
    # 员工在职状态
    status = db.Column(db.Boolean,default = True)


# 添加测试账户 -- 超级管理员
# @app.route('/add')
# def add():
#     user = Users()
#     user.username = 'admin'
#     user.userpwd = 'admin'
#     user.jop = 'admin'
#     user.status = True
#     db.session.add(user)
#     return 'ok'
#



@app.route('/01-login',methods = ['GET','POST'])
def login():
    if request.method =='GET':
        return render_template('01-login.html')
    else:
        result = db.session.query(Users).filter(Users.status ==True)
        if 'text' in request.form:
            if 'name' in request.form:
                name = request.form['name']
                pwd = request.form['pwd']
                for r in result:
                    if r.userpwd == pwd:
                        # userpwd = db.session.query(Users.id).filter(Users.username == name)
                        # username = db.session.query(Users.id).filter(Users.userpwd == pwd)
                        # print(userpwd)
                        # print(username)
                        # print(name)
                        return redirect("/02")
                return redirect("/01-login")
            return redirect("/01-login")


@app.route('/02')
def test():
    return render_template('text02.html',params =locals())


if __name__ == "__main__":
    manager.run()
















