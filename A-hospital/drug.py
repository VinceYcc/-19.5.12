from flask import Flask,request,render_template,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from sqlalchemy import or_
import math,json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123456@127.0.0.1:3306/hospital"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app,db)

manager.add_command('db', MigrateCommand)

class Drug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False,unique=True)
    pro = db.Column(db.String(80), nullable=False)
    num = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer,nullable=False)


db.create_all()










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


# show界面 二级页面
@app.route('/show')
def show():
    return render_template('show.html')

@app.route('/drugview')
def drug():
    return render_template('drugview.html')


if __name__ == '__main__':
    manager.run()