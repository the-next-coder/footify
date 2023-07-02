from concurrent.futures import thread
import re,os,smtplib,datetime,jwt,logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread
import requests
import random,json
from flask import render_template, redirect, request, session, url_for, flash,current_app
from werkzeug.security import generate_password_hash, check_password_hash
from footifyapp import app,db,Message,mail
from footifyapp.models import User,State,Product,Product_category,Cart_item,Order,Order_details,Payment,Shipping_details,Review_order

@app.route('/')
def home():
    products = Product.query.order_by(Product.product_name.desc()).limit(12)
    categories = Product_category.query.all()
    if session.get('user') != None:
        cust_id = session['user']
        cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
        return render_template('user/home.html',products=products,cart_deets=cart_deets,categories=categories)
    else:
        return render_template('user/home.html',products=products,categories=categories)
    
@app.route('/all-products')
def all_products():
    allproducts = Product.query.all()
    if session.get('user') != None:
        cust_id = session['user']
        cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
        return render_template('user/all_products.html',allproducts=allproducts,cart_deets=cart_deets)
    else:
        return render_template('user/all_products.html',allproducts=allproducts)
    
@app.route('/product-category/<id>')
def product_category(id):
    cat_id = Product_category.query.get_or_404(id)
    prod_cat = Product.query.filter(Product.product_catid==cat_id.category_id).all()
    if session.get('user') != None:
        cust_id = session['user']
        cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
        return render_template('user/product_category.html',prod_cat=prod_cat,cart_deets=cart_deets)
    else:
        return render_template('user/product_category.html',prod_cat=prod_cat)

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == 'GET':
        return render_template('user/signup.html')
    else:
        fname = request.form.get('firstname')
        lname = request.form.get('lastname')
        email = request.form.get('emailaddress')
        pwd = request.form.get('password')
        hashed_pwd = generate_password_hash(pwd)
        if email != "" and pwd != "" and fname != "" and lname != "":
            u = User(user_fname=fname,user_lname=lname,user_email=email,user_pwd=hashed_pwd)
            db.session.add(u)
            db.session.commit()
            #getting the id of the newly inserted record
            userid = u.user_id
            #keeping the id in session
            session['user'] = userid
            flash("Your registration was successful!")
            return redirect(url_for('dashboard'))
        else:
            flash("You must complete all the fields to signup")
            return redirect(url_for('login'))

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('user/login.html')
    else:
        email = request.form.get('emailaddress')
        pwd = request.form.get('password')
        user_deets = db.session.query(User).filter(User.user_email==email).first()
        if user_deets != None:
            pwd_indb = user_deets.user_pwd
            #compare with plain password from the form
            pwd_chk = check_password_hash(pwd_indb,pwd)
            if pwd_chk:
                id = user_deets.user_id
                session['user'] = id
                return redirect(url_for('home'))
            else:
                flash("Invalid credentials")
                return redirect(url_for('login'))
        else:
            flash("Invalid credentials")
            return redirect(url_for('login'))

@app.route('/forgot-password/',methods=['POST','GET'])
def forgot_password():
    if request.method == 'GET':
        return render_template('user/forgot_password.html')
    else:
        email = request.form.get('email')
        user_email = User.query.filter(User.user_email==email).first()
        if user_email:
            jwt_token = jwt.encode({'user':email,'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=10)}, current_app.config['SECRET_KEY'], algorithm='HS256')
            reset_link = url_for('password_reset', token=jwt_token, _external=True)
            def send_link(app,msg):
                with app.app_context():
                    mail.send(msg)
            msg = Message(subject = "Password Reset Request", recipients=[email], body=f"Dear {email},\n\nYou requested to reset your password, if this is you please click the link below and follow the instructions to reset your password.\n\n{reset_link} (expires in 10mins).\n\nHowever if this wasn\'t your action, you may need to change your password as someone might be trying to manipulate your credentials. Check and secure your account now.\n\nBest regards,\nFootify.",sender="bashumar291@gmail.com")
            Thread(target=send_link, args=(app,msg)).start()
            flash(f"Password reset link has been sent to {email}", category='success')
            return redirect(url_for('forgot_password'))
        else:
            flash(f"{email} does not exist in our records, please try again")
            return redirect(url_for('forgot_password'))

@app.route('/password-reset/',methods=['POST','GET'])
def password_reset():
    if request.method == 'POST':
        newpwd = request.form.get('newpwd')
        token = request.form.get('token')
        if token != None and newpwd != "":
            try:
                email = jwt.decode(token, current_app.config['SECRET_KEY'],algorithms=['HS256'])['user']
            except jwt.exceptions.DecodeError:
                flash('Token not valid')
                return redirect(url_for('password_reset'))
            user_deets = User.query.filter(User.user_email==email).first()
            if user_deets:
                hashed_newpwd = generate_password_hash(newpwd)
                user_deets.user_pwd = hashed_newpwd
                db.session.commit()
                flash("Password updated successfully,<br> you can now login with your new password!", category='success')
                return redirect(url_for('password_reset'))
            else:
                flash("Email doesn\'t exist", category='error')
                return redirect(url_for('password_reset'))
        else:
            flash("Please complete the form")
            return redirect(url_for('password_reset'))
    else:
        token = request.args.get('token')
        if not token:
            logging.error('Token missing')
            return redirect(url_for('login'))
        try:
            email = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['user']
            user_deets = User.query.filter(User.user_email==email).first()
            if user_deets:
                return render_template('user/password_reset.html',token=token)
            else:
                logging.error('Email not found')
                flash('Email not found')
                return redirect(url_for('forgot_password'))
        except jwt.exceptions.DecodeError:
            logging.error('Token not valid')
            flash('Token not valid')
            return redirect(url_for('password_reset'))

@app.route('/dashboard/')
def dashboard():
    if session.get('user') == None:
        return redirect(url_for('login'))   
    else:
        id = session['user']
        deets = db.session.query(User).get(id)
        return render_template('user/dashboard.html',deets=deets)

@app.route('/my-profile/',methods=['POST','GET'])
def my_profile():
    if session.get('user') == None:
        return redirect(url_for('login'))   
    else:
        if request.method == 'GET':
            deets = db.session.query(User).get(session['user']) 
            states = db.session.query(State).all()
            cust_id = session['user']
            cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
            return render_template('user/profile.html',deets=deets,states=states,cart_deets=cart_deets)
        else:
            phone = request.form.get('phone')
            state = request.form.get('state')
            city = request.form.get('city')
            address = request.form.get('address')
            #updating the db
            id = session['user']
            userobj = db.session.query(User).get(id)
            userobj.user_phone = phone
            userobj.user_stateid = state
            userobj.user_city = city
            userobj.user_address = address
            db.session.commit()
            flash("Profile Updated!")
            return redirect(url_for('my_profile'))

@app.route('/logout')
def logout():
    if session.get('user') != None:
        session.pop('user',None)
    return redirect('/')

@app.route('/product-details/<id>')
def product_details(id):
    prod_deets = Product.query.get_or_404(id)
    if session.get('user') != None:
        cust_id = session['user']
        cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
        if cart_deets:
            return render_template('user/product_details.html',cart_deets=cart_deets,prod_deets=prod_deets)
    return render_template('user/product_details.html',prod_deets=prod_deets)

@app.route('/cart')
def my_cart():
    if session.get('user') == None:
        return redirect(url_for('login'))   
    else:
        cust_id = session['user']
        cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
        if cart_deets:
            return render_template('user/my_cart.html',cart_deets=cart_deets)
        else:
            return render_template('user/my_cart.html')

@app.route('/addto-cart/')
def addto_cart():
    if session.get('user') == None:
        return redirect(url_for('login'))   
    else:
        size = request.args.get('size')
        add_qty = request.args.get('quantity')
        prod_price = request.args.get('amount')
        total_amt = request.args.get('total')
        prod_id = request.args.get('prod_id')
        #prod_deets = Product.query.get_or_404(product_id)
        cart_item = Cart_item(cart_item_size=size,cart_item_qty=add_qty,cart_item_price=prod_price,cart_tot_price=total_amt,user_id=session['user'],product_id=prod_id)
        cartdb = db.session.query(Cart_item).filter(Cart_item.product_id==prod_id,Cart_item.user_id==session['user']).first()
        if cartdb:
            newqty = request.args.get('quantity')
            cartdb.cart_item_qty = cartdb.cart_item_qty + int(newqty)
            cartdb.cart_item_price = prod_price
            cartdb.cart_tot_price = cartdb.cart_tot_price + int(total_amt)
            db.session.commit()
        else:
            db.session.add(cart_item)
            db.session.commit()
        flash('Product added to cart!')
        #return redirect(url_for('my_cart'))
        sendback = "<p>Added!</p>"
        return sendback

@app.route('/removefrom-cart/<id>/')
def removefrom_cart(id):
    if session.get('user') == None:
        return redirect(url_for('login'))   
    else:
        cart_obj = Cart_item.query.get_or_404(id)
        db.session.delete(cart_obj)
        db.session.commit()
        flash("Product have been removed from cart")
        return redirect(url_for('my_cart'))
    
@app.route('/checkout/',methods=['POST','GET'])
def checkout():
    if session.get('user') == None:
        return redirect(url_for('login'))   
    else:
        if request.method == 'GET':
            cust_id = session['user']
            cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
            cart_total = db.session.query(db.func.sum(Cart_item.cart_tot_price)).filter(Cart_item.user_id==cust_id).first()
            order_total = cart_total[0] + 700
            userdeets = db.session.query(User).get(session['user'])
            return render_template('user/checkout.html',cart_deets=cart_deets,cart_total=cart_total,order_total=order_total,userdeets=userdeets)
        else:
            #get the total order amount
            cust_id = session['user']
            cart_total = db.session.query(db.func.sum(Cart_item.cart_tot_price)).filter(Cart_item.user_id==cust_id).first()
            order_total = cart_total[0] + 700
            #insert details into order table
            order_deets = Order(order_total_amt=order_total,user_id=session['user'])
            db.session.add(order_deets)
            db.session.commit()
            #generate a session for the order id
            session['order_id'] = order_deets.order_id
            #generate the ref no and keep in session
            refno = int(random.random()*100000000000)
            session['pay_ref'] = refno
            #insert details into order-details table
            cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
            def ordered_items():
                for c in cart_deets:
                    orderdeets = Order_details(size=c.cart_item_size,quantity=c.cart_item_qty,amount=c.cart_item_price,total=c.cart_tot_price,order_refno=refno,order_id=session['order_id'],product_id=c.cart_content.product_id)
                    db.session.add(orderdeets)
            ordered_items()
            db.session.commit()
            return redirect(url_for('confirm_order'))
            
@app.route('/confirm-order/',methods=['POST','GET'])
def confirm_order():
    if session.get('order_id') != None:
        if request.method == "GET":
            cust_id = session.get('user')
            cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
            order = db.session.query(Order).get(session['order_id'])
            order_total = order.order_total_amt
            return render_template('user/confirm_order.html',cart_deets=cart_deets,order=order,order_total=order_total,refno=session['pay_ref'])
        else:
            cust_id = session['user']
            cart_total = db.session.query(db.func.sum(Cart_item.cart_tot_price)).filter(Cart_item.user_id==cust_id).first()
            order_total = cart_total[0] + 700
            #insert payment details into payment table
            p = Payment(amount_paid=order_total,payment_reference=session['pay_ref'],user_id=session.get('user'),order_id=session.get('order_id'))
            db.session.add(p)
            db.session.commit()
            #details of the order
            order_deets = Order.query.get(session['order_id'])
            user_email = order_deets.ordered_by.user_email
            amount = order_deets.order_total_amt * 100
            headers={"Content-Type":"application/json","Authorization":"Bearer sk_test_ebff11074bd6e6efff9fa005f23a0ec308da3aa5"}

            data={"amount":amount,"reference":session['pay_ref'],"email":user_email}

            response = requests.post("https://api.paystack.co/transaction/initialize",headers=headers,data=json.dumps(data))
            rspjson = json.loads(response.text)
            if rspjson['status']==True:
                url = rspjson['data']['authorization_url']
                return redirect(url)
            else:
                return redirect('/confirm-order/')
    else:
        return redirect('/checkout/')
    
@app.route('/paystack')
def paystack():
    refid = session.get('pay_ref')
    if refid == None:
        return redirect('/')
    else:
        #connect to paystack verify
        headers={"Content-Type":"application/json","Authorization":"Bearer sk_test_ebff11074bd6e6efff9fa005f23a0ec308da3aa5"}
        verifyurl = "https://api.paystack.co/transaction/verify/"+str(refid)
        response= requests.get(verifyurl, headers=headers)
        rspjson = json.loads(response.text)
        if rspjson['status']== True:    #payment was successful
            #update payment status to successful
            payobj = db.session.query(Payment).filter(Payment.payment_reference==refid).first()
            payobj.amount_paid = rspjson['data']['amount'] / 100
            payobj.payment_status = "successful"
            db.session.commit()
            #update paid status and payment_id on order table
            id = session.get('order_id')
            orderobj = db.session.query(Order).get(id)
            orderobj.pay_ref = refid
            orderobj.paid_status = '1'
            db.session.commit()
            #delete user cart history
            cust_id = session.get('user')
            cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
            def delete_cart_item():
                for i in cart_deets:
                    db.session.delete(i)
            delete_cart_item()
            db.session.commit()
            #return rspjson
            return redirect(url_for('orders'))
        else:   #payment was not successful
            #update payment status to failed
            payobj = db.session.query(Payment).filter(Payment.payment_reference==refid).first()
            payobj.amount_paid = rspjson['data']['amount'] / 100
            payobj.payment_status = "failed"
            db.session.commit()
            return redirect(url_for('confirm_order'))

@app.route('/orders/')
def orders():
    if session.get('user') == None:
        return redirect(url_for('login'))   
    else:
        cust_id = session['user']
        cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
        cust_id = session['user']
        user_orders = Order.query.filter(Order.user_id==cust_id).all()
        if user_orders:
            order_deets = Order.query.filter(Order.paid_status=='1').all()
            return render_template('user/orders.html',cart_deets=cart_deets,order_deets=order_deets)
        else:
            return render_template('user/orders.html')

@app.route('/order-details/<id>')
def order_details(id):
    if session.get('user') == None:
        return redirect(url_for('login'))   
    else:
        cust_id = session['user']
        cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
        #id = session.get('order_id')
        orderobj = db.session.query(Order).get(id)
        orderdeets = Order_details.query.filter(Order_details.order_id==orderobj.order_id).all()
        return render_template('user/order_details.html',cart_deets=cart_deets,orderdeets=orderdeets,orderobj=orderobj)

@app.route('/search-products',methods=['GET','POST'])
def search_products():
    if request.method == 'GET':
        return render_template('user/search.html')
    else:
        search_results = request.form.get('search')
        if search_results != '':
            products = Product.query.filter(Product.product_name.ilike("%"+search_results+"%")).all()
            if products != None:
                cust_id = session['user']
                cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
                return render_template('user/search_products.html',products=products,cart_deets=cart_deets)
            else:
                flash('No results found!')
                return redirect(url_for('home'))
        else:
            flash("Enter a product name to search")
            return redirect(url_for('home'))

@app.route('/review-order/<id>',methods=['GET','POST'])
def review_order(id):
    if session.get('user') == None:
        return redirect(url_for('login'))   
    else:
        cust_id = session['user']
        cart_deets = Cart_item.query.filter(Cart_item.user_id==cust_id).all()
        if request.method == 'GET':
            orderobj = db.session.query(Order).get(id)
            return render_template('user/review_order.html',cart_deets=cart_deets,orderobj=orderobj)
        else:
            review = request.form.get('review')
            if review !='':
                orderobj = db.session.query(Order).get(id)
                r = Review_order(review_comment=review,user_id=session['user'],order_id=orderobj.order_id)
                db.session.add(r)
                db.session.commit()
                flash("Your review has been sent successfully!")
                return redirect(url_for('orders'))
            else:
                orderobj = db.session.query(Order).get(id)
                flash("Enter a review comment")
                return redirect(url_for('review_order',id=orderobj.order_id))