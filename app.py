from flask_migrate import Migrate
from flask import Flask, render_template, flash, request, redirect, url_for, session
from flask_wtf import FlaskForm 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import PrimaryKeyConstraint
from flask_login import UserMixin, login_user, LoginManager,login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pandas as pd
from flask_login import LoginManager,UserMixin,current_user, login_required, logout_user
import os
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from wtforms.validators import DataRequired
from wtforms import HiddenField
from datetime import datetime
from dateutil import tz
app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///database.sqlite3"
app.app_context().push()
db =SQLAlchemy(app)
app.secret_key= 'secret_key'
migrate=Migrate(app,db)
app.config['UPLOAD_FOLDER']=os.path.join(app.root_path,'static')
login_manager = LoginManager(app)
login_manager.login_view = 'userlogin'

@login_manager.user_loader
def load_user(username):
    return Userlogin.query.filter_by(username=username).first()

class Userlogin(db.Model,UserMixin):
    username=db.Column(db.String(50),primary_key=True, nullable=False,unique=True)
    password=db.Column(db.String(50),nullable=False)
    def is_active(self):
        # Implement your logic to determine if the user is active or not
        return True
    def is_inactive(self):
        # Implement your logic to determine if the user is active or not
        return False
    def get_id(self):
        return self.username

    
class Sellerlogin(db.Model):
    Seller_Username=db.Column(db.String(50),primary_key=True, nullable=False)
    password=db.Column(db.String(50),nullable=False)

class newuser(db.Model):
    Name=db.Column(db.String(50),nullable=False)
    Phone_Number=db.Column(db.String(50),nullable=False)
    UserName=db.Column(db.String(50),primary_key=True, nullable=False)
    Password=db.Column(db.String(50),nullable=False)
    Confirm_Password=db.Column(db.String(50),nullable=False)

class productadd(db.Model):
    product_name = db.Column(db.String(50), primary_key=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(50000), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    image_extension = db.Column(db.String(10), nullable=True)
    category = db.Column(db.String(50), nullable=False)
    expiry_date = db.Column(db.Date, nullable=True)

class addcategory(db.Model):
    categoryname=db.Column(db.String(50), primary_key=True, nullable=False)

class CartItem(db.Model):
    product_name = db.Column(db.String(50), primary_key=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('userlogin.username'), nullable=False)
    product_name_fk = db.Column(db.String(50), db.ForeignKey('productadd.product_name'), nullable=False)

    user = db.relationship('Userlogin', backref='cart_items')
    product = db.relationship('productadd', backref=db.backref('cart_item', lazy='dynamic'))

    def __init__(self, product_name, price, quantity, username):
        self.product_name = product_name
        self.price = price
        self.quantity = quantity
        self.username = username
        self.product_name_fk = product_name
    __table_args__ = (
        PrimaryKeyConstraint('product_name', 'username'),
    )

class YourSearchForm(FlaskForm):
    search_query = StringField('Search Products', validators=[DataRequired()])
    submit = SubmitField('Search')
class SearchForm(FlaskForm):
    search_query = StringField('Search')
    submit = SubmitField('Search')


class Cart:
    def __init__(self,username):
        self.username = username
        self.items = []

    def add_item(self, product_name, price, quantity):
        cart_item = CartItem(product_name=product_name, price=price, quantity=quantity, username=self.username)
        self.items.append(cart_item)

    def calculate_total_price(self):
        total_price = 0
        for item in self.items:
            total_price += float(item.price) * float(item.quantity)
        return total_price



@app.route('/')
def home():
    if 'username' in session:
        return f'Hello, {session["username"]}! <a href="/logout">Logout</a>'
        return 'Welcome! <a href="/login">Login</a>'
    return render_template('homepage.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    # Use the logout_user() function to log the user out
    logout_user()
    
    # Redirect the user to the homepage or login page
    return redirect(url_for('home'))

@app.route('/sellerlogin' , methods=['GET', 'POST'])
def sellerlogin():
    if request.method=='POST':
        Seller_Username = request.form['Seller_Username']
        password = request.form['Password']
        
        user_data = Sellerlogin.query.filter_by(Seller_Username=Seller_Username, password=password).first()
        
        if user_data:
            
           return redirect(url_for('adminlogin1',  Seller_Username=Seller_Username))
        else:
            
            error_message = 'Invalid username or password'
            return render_template('sellerlogin.html', error_message=error_message)
  
    return render_template('sellerlogin.html')


@app.route('/userlogin', methods=['GET', 'POST'])
def userlogin():
    if request.method=='POST':
        username = request.form['Username']
        password = request.form['Password']
        
        user_data = Userlogin.query.filter_by(username=username).first()
        

        if user_data and check_password_hash(user_data.password, password):
           login_user(user_data) 
           return redirect(url_for('mainpage'))
        else:
           
            error_message = 'Invalid username or password'
            return render_template('userlogin.html', error_message=error_message)
    return render_template('userlogin.html', error_message=None)


@app.route('/newuser', methods=['GET', 'POST'])
def newuser1():
    if request.method == 'POST':
        name = request.form['Name']
        phone_number = request.form['Phone-Number']
        username = request.form['UserName']
        password = request.form['Password']
        confirm_password = request.form['Confirm-Password']

        if password != confirm_password:
            error_message = 'Passwords do not match'
            return render_template('newuser.html', error_message=error_message)
        hashed_password =generate_password_hash(password)
        new_user_instance = newuser(Name=name, Phone_Number=phone_number, UserName=username, Password=hashed_password, Confirm_Password=confirm_password)
        db.session.add(new_user_instance)
        db.session.commit()
        user_login_instance = Userlogin(username=username, password=hashed_password)
        db.session.add(user_login_instance)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('userlogin'))

    return render_template('newuser.html', error_message=None)


@app.route('/mainpage')
def mainpage():
    return render_template('mainpage.html')

@app.route('/adminlogin1')
def adminlogin1():
      Seller_Username = request.args.get('Seller_Username')

      return render_template('adminlogin1.html', Seller_Username=Seller_Username)

products=[]

@app.route('/productadd', methods=['GET', 'POST'])
def productadd1():
    categories_from_db = addcategory.query.all()
    category_choices = [addcategory.categoryname for addcategory in categories_from_db]
    if request.method == 'POST':
        product_name= request.form['productName']
        price = float(request.form['productPrice'])
        Quantity = float(request.form['quantity'])
        ProductDescription=request.form['productDescription']
        product_image = request.files['image']
        product_category = request.form['productCategory']
        expiry_date_str = request.form['expiryDate']
      
        image_extension = '.' + product_image.filename.split('.')[-1]
        image_filename = secure_filename(product_name) + '.' + product_image.filename.split('.')[-1]
        image_path = os.path.join( app.config['UPLOAD_FOLDER'],product_image.filename)
        product_image.save(image_path)
        
        
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')    
    
        
        new_product = productadd(product_name= product_name ,price=price ,quantity=Quantity,description=ProductDescription, image_filename=image_filename, image_extension=image_extension,category=product_category,expiry_date=expiry_date)
        
        db.session.add(new_product)
        db.session.commit()
        
        
        products.append(new_product)
        return redirect(url_for('inventory'))
    return render_template('productadd.html', category_choices=category_choices)

import os

def get_image_extension(product_name):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']  
    for ext in image_extensions:
        image_path = os.path.join(app.static_folder, 'product_images', product_name + ext)
        if os.path.exists(image_path):
            return ext
    

@app.route('/inventory')
def inventory():
    products = productadd.query.all()
    categories = {}
        # Filter products based on the search query
    search_form = YourSearchForm()

    for product in products:
        product.total_price = float(product.price) * float(product.quantity)
        product.image_extension = get_image_extension(product.product_name)

        if product.category not in categories:
            categories[product.category] = [product]
        else:
            categories[product.category].append(product)

    current_datetime = datetime.now(tz=tz.tzutc())  

    return render_template('inventory.html', categories=categories, current_datetime=current_datetime,search_form=search_form)




@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    if request.method == 'POST':
        product_name = request.form.get('productName')
        product_price = float(request.form.get('productPrice'))
        product_quantity = request.form.get('quantity') 

        product = productadd.query.filter_by(product_name=product_name).first()
        current_utc_datetime = datetime.utcnow()

        if product:
            if product.expiry_date and product.expiry_date <= current_utc_datetime.date():
                # The product is expired, show a message
                flash("This product has expired and cannot be added to the cart.", "error")
                return redirect(url_for('inventory'))
            else:
                # Check if the user is authenticated
                if current_user.is_authenticated:
                    # Check if the product is already in the user's cart
                    existing_cart_item = CartItem.query.filter_by(
                        product_name=product_name,
                        username=current_user.username
                    ).first()

                    if existing_cart_item:
                        # If the product is already in the cart, update its quantity
                        existing_cart_item.quantity += 1
                    else:
                        # If the product is not in the cart, create a new cart item
                        cart_item = CartItem(
                            product_name=product_name,
                            price=product_price,
                            quantity=1,
                            username=current_user.username
                        )
                        db.session.add(cart_item)

                    db.session.commit()
                    flash("Product added to the cart.", "success")
                else:
                    flash("You need to log in to add items to the cart.", "error")
                return redirect(url_for('cart_view'))
        else:
            flash("Product not found.", "error")
            return redirect(url_for('inventory'))




@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        new_quantity = float(request.form.get('quantity'))

        cart_item = CartItem.query.filter_by(product_name=product_name).first()
        if cart_item:
            cart_item.quantity = new_quantity
            db.session.commit()
    
    return redirect(url_for('cart_view'))

@app.route('/remove_item', methods=['POST'])
def remove_item():
    if request.method == 'POST':
        product_name = request.form.get('product_name')

        cart_item = CartItem.query.filter_by(product_name=product_name).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
    
    return redirect(url_for('cart_view'))


@app.route('/update_product/<product_name>', methods=['GET', 'POST'])
def update_product(product_name):
    # Retrieve the product from the database using the provided product_name
    product = productadd.query.filter_by(product_name=product_name).first()

    if request.method == 'POST':
        # Update the product fields with the form data
        product.product_name = request.form['product_name']
        product.price = float(request.form['product_price'])
        product.quantity = float(request.form['product_quantity'])
        product.description = request.form['product_description']
        product.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')

        # Commit the changes to the database
        db.session.commit()

        # Redirect back to the inventory page
        return redirect(url_for('inventory'))

    # Render the update product template
    return render_template('update_product.html', product=product)





@app.route('/delete_product', methods=['POST'])
def delete_product():
    if request.method == 'POST':
        product_name = request.form.get('product_name')

        # Retrieve the product from the database
        product = productadd.query.filter_by(product_name=product_name).first()

        if product:
            # Delete the product from the database
            db.session.delete(product)
            db.session.commit()
            flash("Product deleted successfully.", "success")
        else:
            flash("Product not found.", "error")

        return redirect(url_for('inventory'))


@app.route('/cart')
@login_required
def cart_view():
    cart_items = CartItem.query.filter_by(username=current_user.username).all()

    
    for item in cart_items:
        product = productadd.query.filter_by(product_name=item.product_name).first()
        if product:
            item.total_price = float(item.price) * float(item.quantity)
            
    
    return render_template('cart.html', cart_items=cart_items)

@app.route('/search', methods=['GET', 'POST'])
def search():
    # Get the search query from the form input
    search_query = request.form.get('search_query')

    if request.method == 'POST' and search_query:
        # Perform the product search using ilike
        search_results = productadd.query.filter(productadd.product_name.ilike(f"%{search_query}%")).all()
    else:
        # Handle the case when no search query is provided or when a GET request is made
        # In this case, display the entire inventory
        search_results = productadd.query.all()
    current_datetime = datetime.now(tz=tz.tzutc())  
    return render_template('search_results.html',  search_results=search_results, current_datetime=current_datetime)

added_categories = []

@app.route('/addcategory', methods=['GET', 'POST'])
def add_category1():
    if request.method == 'POST':
        new_category = request.form.get('CategoryName')

        if new_category:
            # Check if the category already exists in the list
            if new_category in added_categories:
                flash("Category already exists.", "error")
            else:
                # Add the new category to the list
                added_categories.append(new_category)
                flash("Category added successfully.", "success")

                # Add the new category to the database table
                category_record = addcategory(categoryname=new_category)
                db.session.add(category_record)
                db.session.commit()

        return redirect(url_for('productadd1'))
    else:
        flash("Please provide a valid category name.", "error")

    # Query the database to get category choices
    categories_from_db = addcategory.query.all()
    category_choices = [category.categoryname for category in categories_from_db]

    return render_template('addcategory.html', category_choices=category_choices)

@app.route('/delete_category/<category_id>', methods=['POST'])
def delete_category(category_id):
    # Find the category to delete
    category_to_delete = addcategory.query.filter_by(categoryname=category_id).first()

    if category_to_delete:
        # Delete products in the category
        products_to_delete = productadd.query.filter_by(category=category_id).all()
        for product in products_to_delete:
            db.session.delete(product)

        # Delete the category itself
        db.session.delete(category_to_delete)
        db.session.commit()

        flash("Category and associated products deleted successfully.", "success")
    else:
        flash("Category not found.", "error")

    return redirect(url_for('inventory'))

@app.route('/deletecategories', methods=['GET'])
def delete_categories():
    categories = addcategory.query.all()
    return render_template('deletecategory.html', categories=categories)



if __name__ == "__main__" :
    app.run(debug= True)