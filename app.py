import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import error_message, login_required, usd, process_cart, finalprice

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
    order = db.execute("SELECT id, pizza_name, drinks, price, status, street, city, zip FROM myorder WHERE user_id = ?", session["user_id"])
    return render_template("myorder.html", order=order)

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
        #allpizzaorder = [[{'pid': pizzaid, 'extra':choseningredid}]]
  
    chosenpizzaid = None
    chosendrinkid = None
    choseningredid = []
    
    if request.method == "POST":
        #checking if it is a pizza order
        if "pizzaid" in request.form:
            chosenpizzaid = int(request.form.get("pizzaid"))
            choseningredid = [value for value in request.form.getlist('ingredid') if value]
                    
        if "drinkid" in request.form:
            chosendrinkid = int(request.form.get("drinkid"))
            
        #if item id captured adding it to the session dict        
        if chosenpizzaid:
            SelectedPizza = [{'pid': chosenpizzaid, 'extra':choseningredid}]
            session["cart"]["allpizzaorder"].append(SelectedPizza)
        if chosendrinkid:
            session["cart"]["drinks"].append(chosendrinkid)
        

        #Removing pizza from cart session if removal request id captured
        if "removal_pizza_id" in request.form:
            RemoveablePizzaID = int(request.form.get("removal_pizza_id"))
            RemoveableExtra = [value for value in request.form.getlist('removal_extra_id') if value]
                     
            targetList = [{'pid': RemoveablePizzaID, 'extra':RemoveableExtra}]
            for item in session["cart"]["allpizzaorder"]:
                if item == targetList:
                    session["cart"]["allpizzaorder"].remove(targetList)
                    break
        
        #Removing drink from cart session if removal request id captured
        if "removal_drink_id" in request.form:
            RemoveableDrinkID = int(request.form.get("removal_drink_id"))

            for item in session["cart"]["drinks"]:
                if item == RemoveableDrinkID:
                    session["cart"]["drinks"].remove(RemoveableDrinkID)
                    break


        #Retrieving data based on the ids stored in the session, and returning the data to the webpage 
        result = process_cart()
        return result
    
    result = process_cart()
    return result

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

    #Gettin username
    user_namedict = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    username = user_namedict[0]['username']

    #Creating a string out of the ordered drinks
    ordered_drinks = []
    for drink in session["cart"]["drinks"]:
        drinkdata = db.execute("SELECT name FROM drinks WHERE id = ?", drink)
        drinkname = drinkdata[0]["name"]
        ordered_drinks.append(drinkname)
    #Result: Sprite, Coca-Cola, Iced Tea    
    string_ordered_drinks = ', '.join(ordered_drinks)
    
    #Creating string out of pizza names and extra ingredients.
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
    #Result: Mushroom - Onions, Bell Peppers, Spinach; Hawaiian - Olives, Onions; Margherita - 
    string_ordered_pizzas = '\n'.join(ordered_pizzas)

    #Getting the total price
    totalprice = finalprice()

    #Order time
    time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    #Adding order to the db
    db.execute("INSERT INTO myorder (user_id, user_name, pizza_name, drinks, price, time, first_name, last_name, street, city, zip, terms) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], username, string_ordered_pizzas, string_ordered_drinks, totalprice, time, FirstName, LastName, street, city, zipcode, termsandcond)
    
    #clear cart
    session["cart"]["allpizzaorder"] = []
    session["cart"]["drinks"] = []
    
    return redirect("/myorder")

@app.route("/cancelorder", methods=["POST"])
@login_required
def cancelorder():
    #creating the list of 'Order received' list to make sure the user won't be able to cancel other orders
    ListOfOrders = db.execute("SELECT id FROM myorder WHERE user_id = ? AND status = ?", session["user_id"], "Order received")
    cancelledID = int(request.form.get("orderid"))
    print(ListOfOrders)
    print(cancelledID)
    for order in ListOfOrders:
        orderid = order["id"]
        if cancelledID == orderid:
            print("found")
            print(orderid)
        else:
            print("not found")
    return redirect("/myorder")

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
        template_name = "pizzapage.html"
        return render_template(template_name, pizza_page=True, PizzaDetails=PizzaDetails, Ingredients=Ingredients)

