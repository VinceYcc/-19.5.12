from flask import Flask, request, render_template,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask_script import Manager
import json
from flask_migrate import Migrate, MigrateCommand

pymysql.install_as_MySQLdb()

app = Flask(__name__)

# 链接到mysql中flaskDB数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1:3306/hospital'

# 制定不需要信号追踪
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 创建SQLALchemy 实例
# 制定程序的启动模式为调试
app.config['DEBUG'] = True

db = SQLAlchemy(app)
# 创建manage对象并制定要管理的app
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
manage = Manager(app)
# 创建Migrate对象，并制定关联的app和db
migrate = Migrate(app, db)
# 为manager增加数据库的迁移指令
# 为manager 增加一个子命令-db(自定义)，具体操作由MigrateCommand来提供
manage.add_command('db', MigrateCommand)  # 'db为任意取名'


# 创建病人预约库
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
    patient_bed = db.Column(db.Integer,
                            db.ForeignKey('patient_order.patient_id')
                            )
    def to_dic(self):
        dic = {
            'medical_id':self.medical_id,
            'medical_num':self.medical_num,
            'patient_bed':self.patient_bed,
        }
        return dic
db.create_all()
# 病人预约
@app.route('/add_patient',methods=['GET','POST'])
def add_patient():
    if request.method == "GET":
        return render_template("add_patient.html")
    else:
        patient_name = request.form['patient_name']
        patient_age = request.form['patient_age']
        patient_inf = request.form['patient_info']
        users = Patient_order()
        users.patient_name =patient_name
        users.patient_age =patient_age
        users.patient_info = patient_inf
        if 'isActive' not in request.form:
            users.isActive = False
        db.session.add(users)
        # db.session.commit()
        return "预约成功"



@app.route('/check_user')
def user_info():

    return render_template('inhospital.html',params = locals())

# 查看床位使用的情况
@app.route('/inhospital')
def check_person():
    users = Medical_person.query.all()
    # 查询关联的床位号信息
    # patient_person = users.patient_bed.all()
    # list = []
    # for u in users:
    #     list.append(u.to_dic())
    #     print(list)
    # return json.dumps(list)
    return render_template('inhospital.html',params=locals())




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
        return render_template('recive_bed.html')

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
            return render_template('inhospital.html')




if __name__ == "__main__":
    manage.run()
