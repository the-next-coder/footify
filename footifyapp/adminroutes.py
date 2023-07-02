import os
from flask import render_template, redirect, request, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from footifyapp import app, db
from footifyapp.models import Admin,Product_category,Product,User,Order

@app.route('/admin/')
def admin_dashboard():
    if session.get('admin') == None:
        return redirect(url_for('admin_login'))   
    else:
        user_deets = User.query.all()
        order_deets = Order.query.all()
        order_total = db.session.query(db.func.sum(Order.order_total_amt)).filter(Order.paid_status=='1').first()
        return render_template('admin/admin_dashboard.html',user_deets=user_deets,order_deets=order_deets,order_total=order_total)

@app.route('/admin/login',methods=['POST','GET'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin/admin_login.html')
    else:
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        admin_deets = db.session.query(Admin).filter(Admin.username==username).first()
        if admin_deets != None:
            pwd_indb = admin_deets.password
            #compare with plain password from the form
            pwd_chk = check_password_hash(pwd_indb,pwd)
            if pwd_chk:
                id = admin_deets.admin_id
                session['admin'] = id
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Invalid credentials")
                return redirect(url_for('admin_login'))
        else:
            flash("Invalid credentials")
            return redirect(url_for('admin_login'))

@app.route('/admin/change-pwd/',methods=["POST","GET"])
def admin_changepwd():
    if session.get('admin') == None:
        return redirect(url_for('admin_login'))   
    else:
        if request.method == 'GET': 
            return render_template('admin/admin_changepwd.html')
        else:
            username = request.form.get('username')
            oldpwd = request.form.get('oldpwd')
            newpwd = request.form.get('newpwd')
            adminobj = db.session.query(Admin).get(session['admin'])
            if username == adminobj.username:
                pwd_indb = adminobj.password
                hashed_newpwd = generate_password_hash(newpwd)
                pwd_chk = check_password_hash(pwd_indb,oldpwd)
                if pwd_chk:
                    adminobj.password = hashed_newpwd
                    db.session.commit()
                    flash("Password successfully changed!")
                    return redirect(url_for('admin_login'))
                else:
                    flash("Invalid credentials")
                    return redirect(url_for('admin_login'))
            else:
                    flash("Invalid credentials")
                    return redirect(url_for('admin_login'))

@app.route('/admin/manage-orders/')
def manage_orders():
    if session.get('admin') == None:
        return redirect(url_for('admin_login'))   
    else:
        all_orders = db.session.query(Order).all()
    return render_template('admin/manage_orders.html',all_orders=all_orders)

# @app.route('/admin/manage-orders/edit/<id>/',methods=["POST","GET"])
# def edit_order(id):
#     if session.get('admin') == None:
#         return redirect(url_for('admin_login'))   
#     else:
#         if request.method == 'GET':
#             order_deets = Order.query.get_or_404(id)
#             return render_template('admin/edit_order.html',order_deets=order_deets)
#         else:
#             orderid = request.form.get('orderid')
#             newstatus = request.form.get('status')
#             order_obj = db.session.query(Order).get(orderid)
#             order_obj.order_status = newstatus
#             db.session.commit()
#             flash('Topic successfully updated')
#             return redirect('/admin/topics')

@app.route('/admin/manage-users/')
def manage_users():
    if session.get('admin') == None:
        return redirect(url_for('admin_login'))   
    else:
        user_deets = db.session.query(User).all()
        return render_template('admin/manage_users.html',user_deets=user_deets)

@app.route('/admin/insert-product/',methods=['POST','GET'])
def insert_product():
    if session.get('admin') == None:
        return redirect(url_for('admin_login'))   
    else:
        if request.method == 'GET':
            categories = db.session.query(Product_category).all() 
            return render_template('admin/insert_product.html',categories=categories)
        else:
            prod_name = request.form.get('prod_name')
            prod_price = request.form.get('prod_price')
            prod_desc = request.form.get('prod_desc')
            category = request.form.get('cat_id')
            prod_img = request.files['prod_img']
            filename = prod_img.filename
            allowed = ['.png','.jpg','.jpeg']
            if filename != '':
                name,ext = os.path.splitext(filename)
                if ext.lower() in allowed:
                    prod_img.save('footifyapp/static/uploads/'+filename)
                else:
                    flash("File extension not allowed")
            else:
                flash("Please select a picture")
            prod_deets = Product(product_name=prod_name,product_price=prod_price,product_desc=prod_desc,product_catid=category,product_img=filename)
            db.session.add(prod_deets)
            db.session.commit()
            flash('Product Inserted Successfully!')
            return redirect(url_for('insert_product'))

@app.route('/admin/manage-products/')
def manage_products():
    if session.get('admin') == None:
        return redirect(url_for('admin_login'))   
    else:
        prod_deets = db.session.query(Product).all() 
        return render_template('admin/manage_products.html',prod_deets=prod_deets)

@app.route('/admin/manage-products/delete/<id>/')
def delete_product(id):
    if session.get('admin') == None:
        return redirect(url_for('admin_login'))   
    else:
        prodobj = Product.query.get_or_404(id)
        db.session.delete(prodobj)
        db.session.commit()
        flash('Product successfully deleted')
        return redirect(url_for('manage_products'))

@app.route('/admin/manage-categories/',methods=['POST','GET'])
def manage_categories():
    if session.get('admin') == None:
        return redirect(url_for('admin_login'))   
    else:
        if request.method == 'GET':
            cat_details = db.session.query(Product_category).all() 
            return render_template('admin/manage_categories.html',cat_details=cat_details)
        else:
            cat_name = request.form.get('cat_name')
            cat_desc = request.form.get('cat_desc')
            cat_deets = Product_category(category_name=cat_name,category_desc=cat_desc)
            db.session.add(cat_deets)
            db.session.commit()
            flash('Category Created!')
            return redirect(url_for('manage_categories'))

@app.route('/admin/manage-categories/delete/<id>/')
def delete_category(id):
    if session.get('admin') == None:
        return redirect(url_for('admin_login'))   
    else:
        cat_obj = Product_category.query.get_or_404(id)
        db.session.delete(cat_obj)
        db.session.commit()
        flash('Category successfully deleted')
        return redirect(url_for('manage_categories'))

@app.route('/admin/logout')
def admin_logout():
    if session.get('admin') != None:
        session.pop('admin',None)
        return redirect('/admin')
