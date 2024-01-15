import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import error_message, login_required, usd

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///pizza.db")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route("/")
def index():
    pizzas = db.execute("SELECT * FROM pizzas")
    return render_template("index.html", pizzas=pizzas)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    if session.get("_flashes"):
        flashes = session.get("_flashes")
        session.clear()
        session["_flashes"] = flashes
    else:
        session.clear()
     

    # User reached route via POST (as by submitting a form via POST)
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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Logged in.")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

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

@app.route("/myorder")
@login_required
def myorder():
    """show active orders"""
    return render_template("myorder.html")

@app.route("/drinks")
def drinks():
    """list drinks"""
    drink = db.execute("SELECT * FROM drinks")
    return render_template("drinks.html", drink=drink)

@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():

    #Ensure cart exists
    if "cart" not in session:
        session["cart"] = {"allpizzaorder": [], "drinks": []}
        #session["cart"] = {"allpizzaorder": [], "drinks": []}
        #allpizzaorder = [[{'pid': pizzaid}, {'extra':choseningredid}]]
    
    chosenpizzaid = None
    chosendrinkid = None
    choseningredid = []
    
    if request.method == "POST":
        #checking if it is a pizza order
        if "pizzaid" in request.form:
            try:
                chosenpizzaid = int(request.form.get("pizzaid"))
                choseningredid = [value for value in request.form.getlist('ingredid') if value]
                    
            except:
                abort(404)
        
        if "drinkid" in request.form:
            try:
                chosendrinkid = int(request.form.get("drinkid"))
            except:
                abort(404)

        
        
        #if item id captured adding it to the session dict
        
        if chosenpizzaid:
            SelectedPizza = [{'pid': chosenpizzaid, 'extra':choseningredid}]
            session["cart"]["allpizzaorder"].append(SelectedPizza)
        if chosendrinkid:
            session["cart"]["drinks"].append(chosendrinkid)
        
        #iterating over session dict and qerying them one by one, since the 'IN' sql query did not return a value twice.
        #E.g. I added two pizzas of the same kind and the cart only registered it once because. 
        
        pizza_order = []
        for order in session["cart"]["allpizzaorder"]:
            pizza_id = order[0]['pid']
            extra_ingredient_ids = order[0]['extra']

            pizza_name = db.execute("SELECT * FROM pizzas WHERE id = ?", pizza_id)
            extra_ingredients = db.execute("SELECT * FROM ingredients WHERE id IN (?)", extra_ingredient_ids)

            pizza_order.append({'pizza': pizza_name, 'extra':extra_ingredients})

        
        

        drink_order = []
        for drink_id in session["cart"]["drinks"]:
            drink_order.append(db.execute("SELECT * FROM drinks WHERE id = ?", drink_id))
        
        return render_template("cart.html", pizza_order=pizza_order, drink_order=drink_order,)

    
         
    return render_template("cart.html", pizza_order=pizza_order, drink_order=drink_order)

#Creating a dynamic route to handle pizzas
@app.route("/<pizza_route>")
def pizza(pizza_route):
    pizzaroutes_data = db.execute("select route from pizzas")
    pizzaroutes = [row["route"] for row in pizzaroutes_data]
    
    PizzaDetails = db.execute("SELECT * FROM pizzas WHERE route = ?", pizza_route)
    Ingredients = db.execute("SELECT * FROM ingredients")
    if pizza_route not in pizzaroutes:
        abort(404)
    else:
        template_name = f"{pizza_route}.html"
        return render_template(template_name, pizza_page=True, PizzaDetails=PizzaDetails, Ingredients=Ingredients)

