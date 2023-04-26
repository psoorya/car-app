from flask import *
import os
import mysql.connector
from otp import genotp
app=Flask(__name__)
mydb=mysql.connector.connect(host='localhost',user='root',password='admin',db='db_name')
@app.route('/',methods=['GET','POST'])
def index():
    if request.method=="POST":
        name=request.form['name']
        discription=request.form['desc']
        quantity=request.form['qty']
        category=request.form['category']
        price=request.form['price']
        image=request.files['image']
        cursor=mydb.cursor()
        id1=genotp()
        filename=id1+'.jpg'
        cursor.execute('insert into additems(itemid,name,discription,qty,category,price) values(%s,%s,%s,%s,%s,%s)',[id1,name,discription,quantity,category,price])
        mydb.commit()
        
        print(filename)
        path=r"C:\Users\MY PC\Desktop\SPM\static"
        image.save(os.path.join(path,filename))
        print('success')
    return render_template('items.html')
@app.route('/homepage/')
def homepage():
    cursor=mydb.cursor()
    cursor.execute("select * from additems")
    items=cursor.fetchall()
    return render_template('homepage.html',items=items)
app.run()
