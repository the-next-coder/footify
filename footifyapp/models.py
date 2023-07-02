from datetime import datetime
from footifyapp import db

class Admin(db.Model):
    admin_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    username = db.Column(db.String(100),nullable=True)
    password = db.Column(db.String(120),nullable=True)

class User(db.Model):  
    user_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    user_fname = db.Column(db.String(100),nullable=False)
    user_lname = db.Column(db.String(100),nullable=False)
    user_email = db.Column(db.String(120),nullable=False,unique=True)
    user_pwd = db.Column(db.String(120),nullable=True)
    user_phone = db.Column(db.String(120),nullable=True) 
    user_city = db.Column(db.String(120),nullable=True)
    user_datereg= db.Column(db.DateTime(), default=datetime.utcnow)
    user_address = db.Column(db.String(255),nullable=True)
    #foreign keys
    user_stateid = db.Column(db.Integer, db.ForeignKey('state.state_id'))
    #relationships
    user_state = db.relationship("State", backref="state_of_user")

class Product(db.Model):
    product_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    product_name = db.Column(db.String(100),nullable=False)
    product_price = db.Column(db.Float(),nullable=False)
    product_desc = db.Column(db.String(255),nullable=True)
    product_img = db.Column(db.String(120),nullable=True)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)
    #foreign keys
    product_catid = db.Column(db.Integer, db.ForeignKey('product_category.category_id'))
    #relationships
    prod_cat = db.relationship("Product_category",backref="cat_of_prod")

class Product_category(db.Model):
    category_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    category_name = db.Column(db.String(50),nullable=False)
    category_desc = db.Column(db.String(450),nullable=True)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow)

class Cart_item(db.Model):
    cart_item_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    cart_item_size = db.Column(db.Integer,nullable=False)
    cart_item_qty = db.Column(db.Integer,nullable=False)
    cart_item_price = db.Column(db.Float(),nullable=False)
    cart_tot_price = db.Column(db.Float(),nullable=False)
    #foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    #relationships
    cart_owner = db.relationship("User",backref="user_cart")
    cart_content = db.relationship("Product",backref="cart_products")

class Order(db.Model):
    order_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    order_total_amt = db.Column(db.Float(),nullable=False)
    paid_status = db.Column(db.Enum('1','0'),server_default='0')
    order_date = db.Column(db.DateTime(), default=datetime.utcnow)
    #foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    pay_ref = db.Column(db.String(50),nullable=True)
    shipping_id = db.Column(db.Integer, db.ForeignKey('shipping_details.shipping_id'))
    #relationships
    ordered_by = db.relationship("User",backref="user_order")
   

class Order_details(db.Model):
    order_details_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    size = db.Column(db.Integer,nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    amount = db.Column(db.Float(),nullable=False)
    total = db.Column(db.Float(),nullable=False)
    order_refno = db.Column(db.String(50),nullable=False)
    #foreign keys
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    #relationships
    prod_ordered = db.relationship("Product",backref="ordered_prod")
    
class Payment(db.Model):
    payment_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    amount_paid = db.Column(db.Float(),nullable=False)
    mode_of_payment = db.Column(db.Enum('cash','card'),server_default='card',nullable=False)
    payment_status = db.Column(db.Enum('pending','successful','failed'),server_default='pending',nullable=False)
    payment_reference = db.Column(db.String(50),nullable=False)
    date_paid = db.Column(db.DateTime(), default=datetime.utcnow)
    #foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))

class Shipping_details(db.Model):
    shipping_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    shipping_fee = db.Column(db.Float(),nullable=False)
    shipping_address = db.Column(db.String(255),nullable=False)
    date_shipped = db.Column(db.DateTime(), default=datetime.utcnow)
    pickup_date = db.Column(db.DateTime(), default=datetime.utcnow)
    shipping_status = db.Column(db.Enum('1','0'),server_default='0')
    #foreign keys
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    
class Review_order(db.Model):
    review_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    review_comment = db.Column(db.Text(),nullable=False)
    review_date = db.Column(db.DateTime(), default=datetime.utcnow)
    #foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))

class State(db.Model):
    state_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    state_name = db.Column(db.String(100),nullable=False)