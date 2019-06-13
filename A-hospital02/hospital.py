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
    id_card = db.Column(db.String(32), primary_key=True)
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


# 住院管理
class Patient_order(db.Model):
    """
    病人预约床号，
    1：显示为已有病人
    0:显示床位为空
    """
    # 创建病人ID号为主键
    patient_id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(60))
    patient_age = db.Column(db.Integer)
    patient_info = db.Column(db.String(120))
    # 创建一个Boolean值
    # 1代表预约成功
    # 0代表不预约床位,默认值为false表示为一般病症不预约床号
    p_active = db.Column(db.Boolean, default=False)


class Medical_person(db.Model):
    """创建医护人员的管理表"""
    # 设置医护人员处理的病人序号
    medical_id = db.Column(db.Integer, primary_key=True)
    # 给病人选择床位号
    medical_num = db.Column(db.Integer)
    # 关联病人与床位号的信息
    patient_bed = db.Column(db.Integer)
    def to_dic(self):
        dic = {
            'medical_id':self.medical_id,
            'medical_num':self.medical_num,
            'patient_bed':self.patient_bed,
        }
        return dic
class Medical_mange(db.Model):
    """
    添加病人床位信息
    """
    patient_id = db.Column(db.Integer,
                           db.ForeignKey('patient_order.patient_id')
                           )
    patient_bed = db.Column(db.String(30),primary_key=True)

    medical_num = db.Column(db.Integer)



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
            "text":"该药品已存在"
        }
    else:
        dic = {
            "status":0,
            "text":"可以添加"
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
    if 'name' in request.args:
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
        if drug:
            drug.name = request.form['uname']
            drug.pro = request.form['upro']
            drug.num = request.form['unum']
            drug.price = request.form['uprice']
            db.session.add(drug)
            return redirect('/drugview')
        else:
            return "药品编号未找到，请先添加。"




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
    if 'name' in request.args:
        name = request.args['name']
    return render_template('show.html',params=locals())

@app.route('/switch')
def switch():
    return render_template('01-login.html',params=locals())

@app.route('/exit')
def exit():
    return render_template('01-login.html',params=locals())

@app.route('/personal')
def personal():
    name = request.args['name']
    res = db.session.query(Users).filter(Users.username == name)

    return render_template('personal.html',params=locals())



#门诊界面，操作界面-------------------------------------------------------

@app.route("/2level")
def level_2():
    return render_template("2level.html",params=locals())


@app.route('/check')
def test():
    if 'name' in request.args:
        name=request.args['name']
    return render_template('check.html',params=locals())


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
    if 'name' in request.args:
        name=request.args['name']

    return render_template("register.html",params=locals())


@app.route("/reg")
def reg():
    id_card = request.args["id_card"]
    res = db.session.query(Sick_list).filter_by(id_card=id_card).all()
    if res:
        result = []
        for u in res:
            result.append(u.to_dict())
        return json.dumps(result)
    else:
        return "0"


@app.route("/reg1")
def reg1():
    if 'name' in request.args:
        name=request.args['name']
    id_card = request.args["id_card"]
    s_name = request.args["s_name"]
    s_addr = request.args["s_addr"]
    s_tel = request.args["s_tel"]
    s_in_date = request.args["s_in_date"]
    result = db.session.query(Sick_list).filter_by(id_card=id_card).first()
    if result:
        result.s_in_date = s_in_date
        db.session.commit()
    else:
        sicker = Sick_list()
        sicker.id_card = id_card
        sicker.s_name = s_name
        sicker.s_addr = s_addr
        sicker.s_tel = s_tel
        sicker.s_in_date = s_in_date
        try:
            db.session.add(sicker)
            db.session.commit()
            return render_template("register.html",params=locals())
        except:
            return render_template("register.html",params=locals())



# 住院------------------------------------------------------------
@app.route('/add_01')
def add_01():
    if 'name' in request.args:
        name = request.args['name']

    return render_template('add_bed.html',params = locals())


@app.route('/add_bed',methods=['GET','POST'])
def add_bed():
    # 接收一个床位号进行判断是否占用
    if request.method == 'GET':
        if 'name' in request.args:
            name = request.args['name']
        return render_template('add_bed.html',params = locals())

    else:
        beds = Medical_mange()
        blist = []
        plist = []
        p01list = []
        patient_bed = request.form['bed_id']
        patient_id = request.form['patient_id']
        medical_num = request.form['medical_num']
        patient = db.session.query(Patient_order).all()
        print('patient:',patient)

        patient_id01 = db.session.query(Medical_mange).all()
        print("patient_id01:",patient_id01)
        patient_beds = db.session.query(Medical_mange).filter_by(patient_bed=patient_bed).all()

        for p in patient_id01:
            p01list.append(p.patient_id)
        print('p01list:',p01list)
        for b in patient_beds:
            blist.append(b.patient_bed)
        for p in patient:
            plist.append(p.patient_id)
        print(plist)
        print(blist)
        try:
            # if patient_bed in blist or patient_id in plist:
            #     return "床位已被使用"

            if patient_bed in blist:
                return "床位已被使用"
            # elif p
            elif patient_id in plist:
                return "未找到病人"
            else:
                if patient_id in p01list:
                    return '病人已入住'
                else:
                    # return redirect('/add_bed')
                    beds.patient_bed = patient_bed
                    beds.patient_id = patient_id
                    beds.medical_num = medical_num
                    db.session.add(beds)
            return "添加床位成功"

        except:
                return redirect('/inhospital',params=locals())






#申请出院，根据病人id号删除
# @app.route('/del_patient',methods=['GET','POST'])
# def del_person():
#     if request.method == "GET":
#         return render_template('check_all.html',params=locals())
#     else:
#         # plist = []
#         # blist = []
#         # del_pid = request.form['patient_id']
#         del_bed = request.form['patient_bed']
#         users01 = db.session.query(Medical_mange).filter_by(patient_id=del_bed)
#         # users02 = Medical_mange.query.filter_by(patient_id=del_bed)
#         # for p in users01:
#         #     plist.append(p.patient_id)
#         # for b in users02:
#         #     blist.append(b.patient_bed)
#         # if p in plist or b in blist:
#         #     del users01,users02
#         #     return '办理出院手续成功'
#         # else:
#         #     return "办理手续失败"
#         db.session.delete(users01)
#         # db.session.commit()
#         return '成功'
#




@app.route('/add_patient',methods=['GET','POST'])
def add_patient():
    if request.method == "GET":
        if 'name' in request.args:
            name = request.args['name']
        return render_template("add_patient.html",params=locals())
    else:
        patient_name = request.form['patient_name']
        patient_age = request.form['patient_age']
        patient_inf = request.form['patient_info']
        users = Patient_order()
        users.patient_name =patient_name
        users.patient_age =patient_age
        users.patient_info = patient_inf
        if 'isActive' in request.form:
            # users.isActive = True
            patient_isActice = request.form['isActive']
            if patient_isActice:
                users.p_active=True
            else:
                users.p_active=False
        db.session.add(users)
        # db.session.commit()

        return "预约成功"



@app.route('/check_user')
def user_info():
    if 'name' in request.args:
        name=request.args['name']

    return render_template('inhospital.html',params = locals())

# 查看床位使用的情况
@app.route('/inhospital')
def check_person():
    if 'name' in request.args:
        name=request.args['name']
    users = Medical_mange.query.all()
    # 查询关联的床位号信息
    # patient_person = users.patient_bed.all()
    # list = []
    # for u in users:
    #     list.append(u.to_dic())
    #     print(list)
    # return json.dumps(list)
    return render_template('inhospital.html',params=locals())


@app.route('/check_all')
def user_all():
    if 'name' in request.args:
        name=request.args['name']
    return render_template('check_all.html',params = locals())

# 查看床位使用的情况
@app.route('/check_infor')
def check_all():
    use = db.session.query(Patient_order).all()
    # 查询关联的床位号信息
    # patient_person = users.patient_bed.all()
    # list = []
    # for u in users:
    #     list.append(u.to_dic())
    #     print(list)
    # return json.dumps(list)
    print(use)
    return render_template('check_all.html',params=locals())




# 使用药品情况
# class Pay_drug(db.Model):
#     drug_name = db.Column(db.String(200))
#     drug_price = db.Column(db.Integer)
#     patient_id = db.Column(db.Integer,
#                            db.ForeignKey('patient_id')
#                            )


# 查看医院床位情况,接受一个床号，查看是已否使用
@app.route('/recive_bed',methods=['GET','POST'])
def recive_id_bed():
    # 接收一个床位号进行判断是否占用
    if request.method == 'GET':
        if 'name' in request.args:
            name = request.args['name']
        return render_template('recive_bed.html',params=locals())

    else:
        beds = Medical_person()
        medical_bed = request.form['bed_id']
        users = db.session.query(medical_num=medical_bed).first()
        if users:
            return "已被使用"
        else:
            beds.medical_num = medical_bed
            db.session.add(beds)
            db.session.commit()
            return render_template('inhospital.html',params=locals())

"""
# 出院
@app.route('/outhospital')
def out_hospital():
    return render_template('outhospital.html',params=locals())
#
# @app.route('/out_hspital')
def check_out_person():
    users = Medical_mange.query.all()
    # 查询关联的床位号信息
    # patient_person = users.patient_bed.all()
    # list = []
    # for u in users:
    #     list.append(u.to_dic())
    #     print(list)
    # return json.dumps(list)
    return render_template('outhospital.html',params=locals())
"""




if __name__ == "__main__":
    manager.run()
