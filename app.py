import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, abort, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import secrets
from helpers import login_required, usd, process_cart, finalprice
from flask_admin import Admin, AdminIndexView, expose
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from wtforms import SelectField
from flask_admin.menu import MenuLink

# Configure application.
app = Flask(__name__)
# Configure session to use filesystem (instead of signed cookies).
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# Configure QSLAlchemy for admin page use
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pizza.db"
dba = SQLAlchemy(app)

# Defining status for display on admin index.
def in_progress_orders():
    return Order.query.filter_by(status='In progress').count()
def order_received_orders():
    return Order.query.filter_by(status='Order received').count()

# Reducing accessibility to admin page.
class SecuredHomeView(AdminIndexView):
    def is_accessible(self):
        return session.get("user_type") == "admin"
    
    @expose('/')                                                                   
    def index(self):  
        in_progress = in_progress_orders()
        received = order_received_orders()
        print(in_progress)                                                       
        return self.render('/admin/index.html', in_progress=in_progress, received=received)

# Creating models for data to access through admin page.
class Order(dba.Model):
    order_id = dba.Column(dba.Integer, primary_key=True)
    status = dba.Column(dba.String)
    user_name = dba.Column(dba.String)
    pizza_name = dba.Column(dba.String)
    drinks = dba.Column(dba.String)
    first_name = dba.Column(dba.String)
    last_name = dba.Column(dba.String)
    city = dba.Column(dba.String)
    zip = dba.Column(dba.String)
    street = dba.Column(dba.String)
    price = dba.Column(dba.Integer)

    __tablename__ = 'myorder'

class Users(dba.Model):
    id = dba.Column(dba.Integer, primary_key=True)
    username = dba.Column(dba.String)
    type = dba.Column(dba.String)
    
    __tablename__ = 'users'

# Creating a customer model view.
class OrderModel(ModelView):
    column_display_pk = True
    column_filters = ("status", "order_id")
    form_overrides = {'status': SelectField}
    form_args = {'status': {'choices': [('Order received'), ('In progress'), ('Delivered'), ('Cancelled')]}}

    def is_accessible(self):
        return session.get("user_type") == "admin"

class UserModel(ModelView):
    column_display_pk = True
    form_overrides = {'type': SelectField}
    form_args = {'type': {'choices': [('user'), ('admin')]}}

    def is_accessible(self):
        return session.get("user_type") == "admin"

# Configuring admin page.
admin = Admin(app, index_view=SecuredHomeView(url='/admin'), template_mode='bootstrap3')
admin.add_view(OrderModel(Order, dba.session))
admin.add_view(UserModel(Users, dba.session))

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///instance/pizza.db")
print(db)

# Error handlig for non-existing URLs.
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route("/")
def index():
    pizzas = db.execute("SELECT img, name, price, ingredients, route FROM pizzas")
    return render_template("index.html", pizzas=pizzas)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id while preservin flashed message
    if session.get("_flashes"):
        flashes = session.get("_flashes")
        session.clear()
        session["_flashes"] = flashes
    else:
       session.clear()

    # User reached route via POST
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please enter a username.")
            return redirect("/login")
            
        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter a password.")
            return redirect("/login")
        
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_type"] = rows[0]["type"]

        # Redirect user to home page
        flash("Logged in.")
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("login.html")

# Registering user.
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        usersdict = db.execute("SELECT username FROM users")
        user = []
        for row in usersdict:
            user.append(row["username"])

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please provide a username.")
            return redirect("/register")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter a password.")
            return redirect("/register")
            
        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            flash("Please enter a password confirmation.")
            return redirect("/register")
        
        elif request.form.get("username") in user:
            flash("The username is alredy taken.")
            return redirect("/register")
            
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("The password confirmation is incorrect")
            return redirect("/register")
            
        else:
            db.execute(
                "INSERT INTO users (username, hash) VALUES(?, ?)",
                request.form.get("username"),
                generate_password_hash(request.form.get("password")),
            )
            flash("Successfully registered. Please log in.")
            return redirect("/login")
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Logged out.")
    return redirect("/")

# Listing user order.
@app.route("/myorder")
@login_required
def myorder():
    """show active orders"""
    order = db.execute("SELECT order_id, pizza_name, drinks, price, status, street, city, zip FROM myorder WHERE user_id = ?", session["user_id"])
    return render_template("myorder.html", order=order)

# returning Json for AJAX request.
@app.route("/myorderdata")
@login_required
def myorderdata():
    order = db.execute("SELECT order_id, pizza_name, drinks, price, status, street, city, zip FROM myorder WHERE user_id = ?", session["user_id"])
    return jsonify(order)

# drink page
@app.route("/drinks")
def drinks():
    """list drinks"""
    # creating tokens not to submit the same form two times if the user navigates back after submit.
    drinktoken = secrets.token_hex(16)
    session['drink_token'] = drinktoken
    drink = db.execute("SELECT * FROM drinks")
    return render_template("drinks.html", drink=drink, drinktoken=drinktoken)


@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():

    #Ensure cart exists
    if "cart" not in session:
        session["cart"] = {"allpizzaorder": [], "drinks": []}
    
    #initializing values not to get error if variables are empty.
    chosenpizzaid = None
    chosendrinkid = None
    choseningredid = []
    
    if request.method == "POST":
        # Token is removed after the item is added to the cart once, in order to prevent caching POST request.
        if request.form.get('form_token') == session.pop('form_token', None):
            
            pizzaidsquery = db.execute("SELECT id FROM pizzas")
            extraidsquery = db.execute("SELECT id FROM ingredients")
            drinkidsquery = db.execute("SELECT id FROM drinks")
            
            # Checking if it is a pizza order.
            if "pizzaid" in request.form:
                
                chosenpizzaid = int(request.form.get("pizzaid"))
                choseningredid = [value for value in request.form.getlist('ingredid') if value]

                # Check if selected pizza is in the pizza list.
                pizzaids = [row['id'] for row in pizzaidsquery]
                if chosenpizzaid not in pizzaids:
                    flash("Do not manipulate pizza IDs!")
                    return redirect("/")

                # Check if selected ingred is in the ingred list.
                extraids = [row['id'] for row in extraidsquery]
                for eid in choseningredid:
                    if int(eid) not in extraids:
                        flash("Do not manipulate ingredient IDs!")
                        return redirect("/")
                        
            if "drinkid" in request.form:
                if request.form.get('drink_token') == session.pop('drink_token', None):
                    chosendrinkid = int(request.form.get("drinkid"))
                    
                    # Check if selected drink is in the drink list.
                    drinkids = [row['id'] for row in drinkidsquery]
                    if chosendrinkid not in drinkids:
                        flash("Do not manipulate drink IDs!")
                        return redirect("/")
                
            # If item id captured adding it to the session dict        
            if chosenpizzaid:
                SelectedPizza = [{'pid': chosenpizzaid, 'extra':choseningredid}]
                session["cart"]["allpizzaorder"].append(SelectedPizza)
            if chosendrinkid:
                session["cart"]["drinks"].append(chosendrinkid)
            

            # Removing pizza from cart session if removal request id captured.
            if "removal_pizza_id" in request.form:
                RemoveablePizzaID = int(request.form.get("removal_pizza_id"))
                RemoveableExtra = [value for value in request.form.getlist('removal_extra_id') if value]
                        
                targetList = [{'pid': RemoveablePizzaID, 'extra':RemoveableExtra}]
                for item in session["cart"]["allpizzaorder"]:
                    if item == targetList:
                        session["cart"]["allpizzaorder"].remove(targetList)
                        break
            
            # Removing drink from cart session if removal request id captured.
            if "removal_drink_id" in request.form:
                RemoveableDrinkID = int(request.form.get("removal_drink_id"))

                for item in session["cart"]["drinks"]:
                    if item == RemoveableDrinkID:
                        session["cart"]["drinks"].remove(RemoveableDrinkID)
                        break

            
            # Retrieving data based on the ids stored in the session, and returning the string represenation of ids to the webpage. 
            result = process_cart()
            return result
        
        else:
            return redirect("/cart")
    
    result = process_cart()
    return result

# Handling orders, gettin user details.
@app.route("/order", methods=["POST"])
@login_required
def order():
    if not request.form.get("FirstName"):
        flash("Please fill in all fields.")
        return redirect("/cart")
    else:
        FirstName = request.form.get("FirstName")

    if not request.form.get("LastName"):
        flash("Please fill in all fields.")
        return redirect("/cart")
    else:
        LastName = request.form.get("LastName")

    if not request.form.get("street"):
        flash("Please fill in all fields.")
        return redirect("/cart")
    else:
        street = request.form.get("street")

    if not request.form.get("city"):
        flash("Please fill in all fields.")
        return redirect("/cart")
    else:
        city = request.form.get("city")

    if not request.form.get("zip"):
        flash("Please fill in all fields.")
        return redirect("/cart")
    else:
        zipcode = request.form.get("zip")
   
    if not request.form.get("termsandcond"):
        flash("Please accept the TERMS.")
        return redirect("/cart")
    else:
        termsandcond = request.form.get("termsandcond")

    # Getting username.
    user_namedict = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    username = user_namedict[0]['username']

    # Creating a string out of the ordered drinks.
    ordered_drinks = []
    for drink in session["cart"]["drinks"]:
        drinkdata = db.execute("SELECT name FROM drinks WHERE id = ?", drink)
        drinkname = drinkdata[0]["name"]
        ordered_drinks.append(drinkname)
    # Result e.g.: Sprite, Coca-Cola, Iced Tea    
    string_ordered_drinks = ', '.join(ordered_drinks)
    
    # Creating string out of pizza names and extra ingredients.
    ordered_pizzas = []
    for plist in session["cart"]["allpizzaorder"]:
        ingredients = []
        pizzadata = db.execute("SELECT name FROM pizzas WHERE id = ?", plist[0]['pid'])
        pizzaname = pizzadata[0]["name"]    
        for ingred in plist[0]['extra']:
            ingreddata = db.execute("SELECT name FROM ingredients WHERE id = ?", ingred)
            ingredname = ingreddata[0]["name"]
            ingredients.append(ingredname)
        string_ingreds = ', '.join(ingredients)
        pizzawithingred = pizzaname + " - " + string_ingreds
        ordered_pizzas.append(pizzawithingred)
    # Result e.g.: Mushroom - Onions, Bell Peppers, Spinach; Hawaiian - Olives, Onions; Margherita - 
    string_ordered_pizzas = '; '.join(ordered_pizzas)

    # Getting the total price for the order.
    totalprice = finalprice()

    # Order time.
    time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Adding order to the db.
    db.execute("INSERT INTO myorder (user_id, user_name, pizza_name, drinks, price, time, first_name, last_name, street, city, zip, terms) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], username, string_ordered_pizzas, string_ordered_drinks, totalprice, time, FirstName, LastName, street, city, zipcode, termsandcond)
    
    # Clear cart.
    session["cart"]["allpizzaorder"] = []
    session["cart"]["drinks"] = []
    
    return redirect("/myorder", code=302)

# Allowing user to cancel orders with status 'Order received'.
@app.route("/cancelorder", methods=["POST"])
@login_required
def cancelorder():
    # Creating the list of 'Order received' list to make sure the user won't be able to cancel other orders.
    Orderdata = db.execute("SELECT order_id FROM myorder WHERE user_id = ? AND status = ?", session["user_id"], "Order received")
    ListOfOrders = [row["order_id"] for row in Orderdata]
    cancelledID = int(request.form.get("orderid"))
    if cancelledID not in ListOfOrders:
        flash("You can only cancel orders with 'Order received' status.")
        return redirect("/myorder")
    else:
        db.execute("UPDATE myorder SET status = ? WHERE user_id = ? AND order_id = ?", "Cancelled", session["user_id"], cancelledID)

    return redirect("/myorder")

#Creating a dynamic route to handle pizzas.
@app.route("/<pizza_route>")
def pizza(pizza_route):
    pizzaroutes_data = db.execute("SELECT route FROM pizzas")
    pizzaroutes = [row["route"] for row in pizzaroutes_data]
    # Tokens in order to prevent double posting after navigating back after an order.
    token = secrets.token_hex(16)
    session['form_token'] = token
    
    PizzaDetails = db.execute("SELECT id, name, ingredients, img, price FROM pizzas WHERE route = ?", pizza_route)
    Ingredients = db.execute("SELECT * FROM ingredients")
    if pizza_route not in pizzaroutes:
        abort(404)
    else:
        template_name = "pizzapage.html"
        return render_template(template_name, PizzaDetails=PizzaDetails, Ingredients=Ingredients, token=token)

