from flask import Flask, render_template, request, redirect
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import math
# import pymysql
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func, and_

app = Flask(__name__)
# 首先链接数据库库名Users
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123456@127.0.0.1/hospital"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 指定为调试模式
app.config['DEBUG'] = True
# 制定执行完增删改查之后的自动提交
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# 创建SQLALchemy的实例
db = SQLAlchemy(app)
# 创建Manager对象并制定要挂不努力的app
manager = Manager(app)

# 创建Migrate的对象，并制定关联的app和db

migrate = Migrate(app, db)

# 为manager增加数据库的迁移指令
# 为manager 增加一个自命令-db，具体操作由MigrateCommand
manager.add_command('db', MigrateCommand)


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, index=True)
    userpwd = db.Column(db.String(100), nullable=False)
    # 工作岗位
    jop = db.Column(db.String(100), nullable=False, index=True)
    # 员工在职状态
    status = db.Column(db.Boolean, default=True)


class Sick_list(db.Model):
    __tablename__ = "sick_list"
    id_card = db.Column(db.Integer, primary_key=True)
    s_name = db.Column(db.String(30), nullable=False, index=True)
    s_addr = db.Column(db.String(128), nullable=True)
    s_tel = db.Column(db.Integer, unique=True)
    s_in_date = db.Column(db.String(64))

    def to_dict(self):
        dict = {
            'id_card': self.id_card,
            's_name': self.s_name,
            's_addr': self.s_addr,
            's_tel': self.s_tel,
            's_in_date': self.s_in_date
        }
        return dict

class Drug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False,unique=True)
    pro = db.Column(db.String(80), nullable=False)
    num = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer,nullable=False)

db.create_all()


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

@app.route('/01-login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        result = db.session.query(Users).filter(Users.status == True)
        if 'text' in request.form:
            if 'name' in request.form:
                name = request.form['name']
        return render_template('01-login.html',params=locals())
    else:
        result = db.session.query(Users).filter(Users.status == True)
        if 'text' in request.form:
            if 'name' in request.form:
                name = request.form['name']
                pwd = request.form['pwd']
                for r in result:
                    if r.userpwd == pwd:
                        return render_template('show.html',params= locals())
                return redirect("/01-login")
            return redirect("/01-login")

# 药库页面界面 二级页面-------------------------------------------------------------
@app.route("/checkuname")
def checkuname():
    uname = request.args['uname']
    drug = Drug.query.filter_by(name=uname).first()
    if drug:
        dic = {
            "status":1,
            "text":"uname already exist"
        }
    else:
        dic = {
            "status":0,
            "text":"uname does not exist"
        }
    return json.dumps(dic)

@app.route("/add",methods=['POST'])
def add():
    uid = request.form['uid']
    uname = request.form['uname']
    upro = request.form['upro']
    unum = request.form['unum']
    uprice = request.form['uprice']
    drug = Drug()
    drug.id = uid
    drug.name = uname
    drug.pro = upro
    drug.num = unum
    drug.price = uprice
    try:
        if uid and uname and upro and uname and uprice:
            db.session.add(drug)
            dic = {
                "status":1,
                "text":"添加成功"
            }
        else:
            dic = {
                "status":1,
                "text":"信息不全无法添加"
            }
        return json.dumps(dic)
    except Exception as ex:
        print(ex)
        dic = {
            "status":0,
            "text":"添加失败"
        }
        return json.dumps(dic)

@app.route('/drugview',methods=['GET','POST'])
def page():
    name=request.args['name']
    drugs = db.session.query(Drug)
    if 'kw' in request.args:
        kw = request.args['kw']
        drugs = drugs.filter(
            or_(
                Drug.name.like('%' + kw + '%'),
                Drug.pro.like('%' + kw + '%')
            )
        )
    pageSize = 15
    currentPage = int(request.args.get('currentPage',1))
    ost = (currentPage-1)*pageSize
    drugs = drugs.offset(ost).limit(pageSize).all()
    totalCount = db.session.query(Drug).count()
    lastPage = math.ceil(totalCount/pageSize)
    prevPage = 1
    if currentPage > 1:
        prevPage = currentPage - 1
    nextPage = lastPage
    if currentPage < lastPage:
        nextPage = currentPage + 1

    return render_template("drugview.html",params = locals())



@app.route('/update',methods=['GET','POST'])
def update():
    if request.method == 'GET':
        id = request.args['id']
        drugs = db.session.query(Drug).filter_by(id=id).first()
        return render_template('update.html',params=drugs)
    else:
        id = request.form['uid']
        drug = db.session.query(Drug).filter_by(id=id).first()
        drug.name = request.form['uname']
        drug.pro = request.form['upro']
        drug.num = request.form['unum']
        drug.price = request.form['uprice']
        db.session.add(drug)
        return redirect('/drugview')




@app.route('/delete')
def delete():
    if request.method == 'GET':
        id = request.args['id']
        drugs = db.session.query(Drug).filter_by(id=id).first()
        db.session.delete(drugs)
        return redirect('/drugview')

import flask_excel as excel
excel.init_excel(app)
@app.route('/excel', methods=['GET'])


def exp_excel():
    drugs = db.session.query(
        Drug.id.label('药品编码'),
        Drug.name.label('药品名称'),
        Drug.pro.label('药品厂商'),
        Drug.num.label('药品数量'),
        Drug.price.label('药品价格')
    ).order_by(Drug.id).all()
    return excel.make_response_from_query_sets(
        drugs,
        column_names=[
            '药品编码',
            '药品名称',
            '药品厂商',
            '药品数量',
            '药品价格'
        ],
        file_type='xlsx',
        file_name='list.xlsx'
    )


# show界面 二级页面----------------------------------------------
@app.route('/show')
def show():
    name=request.args['name']
    return render_template('show.html',params=locals())

@app.route('/switch')
def switch():
    return render_template('01-login.html')

@app.route('/exit')
def exit():
    return render_template('01-lohin.html')

@app.route('/personal')
def personal():
    name = request.args['name']
    res = db.session.query(Users).filter(Users.username == name)

    return render_template('personal.html',params=locals())


#门诊界面，操作界面-------------------------------------------------------

@app.route("/2level")
def level_2():
    return render_template("2level.html")


@app.route('/check')
def test():
    return render_template('check.html')


@app.route("/check-server")
def check_server():
    if request.args:
        id_card = request.args["id_card"]
        s_name = request.args["s_name"]
        s_addr = request.args["s_addr"]
        s_tel = request.args["s_tel"]
        s_in_date = request.args["s_in_date"]
        result = db.session.query(Sick_list).filter \
            (or_(Sick_list.id_card.like("%" + id_card + "%"),
                 Sick_list.s_name.like("%" + s_name + "%"),
                 Sick_list.s_addr.like("%" + s_addr + "%"),
                 Sick_list.s_tel.like("%" + s_tel + "%"),
                 Sick_list.s_in_date.like("%" + s_in_date + "%"), )).all()
        list_ = []
        for u in result:
            list_.append(u.to_dict())
        return json.dumps(list_)
    else:
        users = Sick_list.query.all()
        list_ = []
        for u in users:
            list_.append(u.to_dict())
        return json.dumps(list_)


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/reg")
def reg():
    id_card = request.args["id_card"]
    res = db.session.query(Sick_list).filter_by(id_card=id_card).all()
    if res:
        result =[]
        for u in res:
            result.append(u.to_dict())
        return json.dumps(result)
    else:
        return "0"



# 住院-----------------------------------------------




if __name__ == "__main__":
    manager.run()
