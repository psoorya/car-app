from flask import Flask,redirect,request,render_template,url_for,flash,session,send_file
from flask_mysqldb import MySQL
from flask_session import Session
from otp import genotp
import stripe
from cmail import sendmail
import os
import mysql.connector
import random
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from tokenreset import token
from io import BytesIO
stripe.api_key='sk_test_51N0e5DSDJvLf5S73pOqhDWCmhY1ZnZoHaZWU7HsvakrSbndaIEH4PB3JoZZpEPcBUA0vQZJBdUq738bpwucZbqRl00fWWba3hn'
app=Flask(__name__)
app.secret_key='JASHFVNASR8FU32@2R'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='db_name'
mydb=mysql.connector.connect(host='localhost',user='root',password='admin',db='db_name')
Session(app)
mysql=MySQL(app)
@app.route('/')
def homepage1():
    cursor=mydb.cursor()
    cursor.execute("select * from additems")
    items=cursor.fetchall()
    return render_template('autosport.html',items=items)

@app.route('/signup',methods=['GET','POST'])
def signin():
    if request.method=='POST':
        username=request.form.get('username')
        emailid=request.form.get('email')
        password=request.form.get('password')        
        cursor=mysql.connection.cursor()
        cursor.execute('select username from users')
        data=cursor.fetchall()
        cursor.execute('select email from users')
        edata=cursor.fetchall()
        
        print(request.form)
        #print(data)
        if (username, ) in data:
            flash('User already exisit')
            return render_template('signup.html')
        if (emailid, ) in edata:
            flash('Email id already exisit')
            return render_template('signup.html')
        cursor.close()
        otp=genotp()
        subject='thanks for registering to the application'
        body=f'use this otp to register {otp}'
        sendmail(emailid,subject,body)
        return render_template('otp.html',otp=otp,username=username,emailid=emailid,password=password)
    else:
        flash('invalid code')
        return render_template('signup.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from users where username=%s and password=%s',[username,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid email or password')
            return render_template('signin.html')
        else:
            session['user']=username
            return redirect(url_for('home'))
    return render_template('signin.html')
@app.route('/Shome')
def home():
    cursor=mydb.cursor()
    cursor.execute("select * from additems")
    items=cursor.fetchall()
    return render_template('autosport.html',items=items)
        #flash('login first')
    #return redirect(url_for('login'))
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('index'))
    else:
        flash('already logged out!')
        return redirect(url_for('login'))
@app.route('/otp/<otp>/<username>/<emailid>/<password>',methods=['GET','POST'])
def otp(otp,username,emailid,password):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mysql.connection.cursor()
            lst=[username,emailid,password]
            query='insert into users values(%s,%s,%s)'
            cursor.execute(query,lst)
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
    return render_template('otp.html',otp=otp,username=username,emailid=emailid,password=password)
@app.route('/forgetpassword',methods=['GET','POST'])
def forgetpassword():
    if request.method=='POST':
        email=request.form['id']
        cursor=mysql.connection.cursor()
        cursor.execute('select email from signup')
        data=cursor.fetchall()
        if (email,) in data:
            cursor.execute('select email from signup where email=%s',[email])
            data=cursor.fetchone()[0]
            cursor.close()
            subject=f'Reset password for {data}'
            body=f'reset the password using -{request.host+url_for("createpassword",token=token(email,120))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('login'))
        else:
            return 'Invalid user email'
    return render_template('forgot.html')
@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):
    try:
        s=Serializer(app.config['SECRET_KEY'])
        email=s.loads(token)['user']
        if request.method=='POST':
            npass=request.form['npassword']
            cpass=request.form['cpassword']
            if npass==cpass:
                cursor=mysql.connection.cursor()
                cursor.execute('update signup set password=%s where email=%s',[npass,email])
                mysql.connection.commit()
                return 'Password reset successfull'
            else:
                return 'password mismatch'
        return render_template('newpassword.html')
    except:
        return 'link expired try again'
@app.route('/adminregister', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        emailid = request.form['emailid']
        cursor = mysql.connection.cursor()
        cursor.execute('select username from admin_users')
        data=cursor.fetchall()
        cursor.execute('select email from admin_users')
        edata=cursor.fetchall()
        # Redirect to login page
        if (username, ) in data:
            flash('user already exisit')
            return render_template('admin_login.html')
        if (emailid, ) in edata:
            flash('Email id already exisit')
            return render_template('admin_login.html')
        cursor.close()
        otp=genotp()
        subject='thanks for registering to the application'
        body=f'use this otp to register {otp}'
        sendmail(emailid,subject,body)
        return render_template('aotp.html',otp=otp,username=username,emailid=emailid,password=password)
    return render_template('admin_register.html')
    
# Admin login page
@app.route('/adminlogin', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin'):
        return redirect(url_for('admin'))
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        
        # Check if user exists in database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT count(*) FROM admin_users WHERE username = %s AND password = %s",[username,password])
        count = cursor.fetchone()[0]
        
        if count==0:
            flash('Invalid email or paassword')
            # Set session variable and redirect to admin dashboard
            return render_template('admin_login.html')
        else:
            # Show error message
            session['user']=username
            return redirect(url_for('admin_login'))
    return render_template('dashboard.html')

@app.route('/otp1/<otp>/<username>/<emailid>/<password>',methods=['GET','POST'])
def otp1(otp,username,emailid,password):
    if request.method=='POST':
        uotp=request.form['otp1']
        if otp==uotp:
            cursor=mysql.connection.cursor()
            lst=[username,emailid,password]
            query='insert into admin_users values(%s,%s,%s)'
            cursor.execute(query,lst)
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('admin_login'))
        else:
            flash('Wrong otp')
    return render_template('aotp.html',otp=otp,username=username,emailid=emailid,password=password)
@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'logged_in' in session:
        return render_template('dashboard.html')
    else:
        # If user is not logged in, redirect to login page
        return redirect(url_for('login'))



@app.route('/addcars',methods=['GET','POST'])
def items():
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
        cursor.execute('insert into additems(car_id,name,discription,qty,category,price) values(%s,%s,%s,%s,%s,%s)',[id1,name,discription,quantity,category,price])
        mydb.commit()
        
        print(filename)
        path=os.path.dirname(os.path.abspath(__file__))
        print(path)
        static_path=os.path.join(path,'static')
        print(static_path)
        image.save(os.path.join(static_path,filename))
        print('success')
    return render_template('items.html')

@app.route('/car_status')
def car_status():
    return render_template('car_status.html')

'''@app.route('/car_booking', methods=['GET', 'POST'])
def car_booking():
    if request.method == 'POST':
        # get form data
        pickup_location = request.form['pickup-location']
        return_location = request.form['return-location']
        pickup_date = request.form['pickup-date']
        pickup_time = request.form['pickup-time']
        return_date = request.form['return-date']
        return_time = request.form['return-time']
        full_name = request.form['full-name']
        age = request.form['age']
        gps = request.form.get('gps', 'no')
        child_seat = request.form.get('child-seat', 'no')

        # insert data into MySQL database
        cursor=mydb.cursor()
        cursor.execute("INSERT INTO car_bookings (pickup_location, return_location, pickup_date, pickup_time, return_date, return_time, full_name, age, gps, child_seat) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (pickup_location, return_location, pickup_date, pickup_time, return_date, return_time, full_name, age, gps, child_seat))
        mysql.connection.commit()
        cursor.close()

        return redirect('/success') # redirect to success page

    return render_template('book form.html')''' # render the car booking form


@app.route('/edit')
def edit():
    #if session.get('admin'):
    cursor=mysql.connection.cursor()
    cursor.execute('select * from additems')
    data=cursor.fetchall()
    cursor.close()
    print(data)
        
    return render_template('car_status.html', data=data)



@app.route('/success')
def success1():
    return 'Booking successful!' # success message

@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/car_booking/<car_id>',methods=['POST','GET'])
def car_booking(car_id):
    if session.get('user'):
       cursor=mydb.cursor()
       cursor.execute("select name,price from additems where car_id=%s",[car_id])
       data_c=cursor.fetchone()
       name=data_c[0]
       price=data_c[1]
       return render_template('book_form.html',car_id=car_id,name=name,price=price)
    else:
        return redirect(url_for('login'))


@app.route('/payment/',methods=['POST'])
def payment():
    if session.get('user'):
        car_id=request.form['car_id']
        name=request.form['name']
        price=int(float(request.form['price']))
        q=1
        total=price
        checkout_session=stripe.checkout.Session.create(
            success_url=url_for('success',car_id=car_id,name=name, price=price,q=q,total=total,_external=True),
            line_items=[
                {
                    'price_data': {
                        'product_data': {
                            'name': name,
                        },
                        'unit_amount': price*100,
                        'currency': 'inr',
                    },
                    'quantity': q,
                },
                ],
            mode="payment",)
        return redirect(checkout_session.url)
    else:
        return redirect(url_for('login'))
@app.route('/success/<car_id>/<name>/<price>/<q>/<total>')
def success(car_id,name,price,q,total):
    if session.get('username'):
        cursor=mydb.cursor(buffered=True)
        
        cursor.execute("insert into orders(car_id,name,qty,price,username) values(%s,%s,%s,%s,%s)",[car_id,name,q,total,session.get('user')])
        mydb.commit()
        return 'Order Placed'
    return redirect(url_for('login'))






app.run(use_reloader=True,debug=True,port='8000')

