from functools import wraps
from flask import render_template, flash
from flask import redirect, render_template, session
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///instance/pizza.db")

def login_required(f):
    """
    Decorate routes to require login.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def process_cart():
    pizza_order = []

    #creating the pizza orders in the session, with the extra ingreds based on values captured.
    for order in session["cart"]["allpizzaorder"]:
        pizza_id = order[0]['pid']
        extra_ingredient_ids = order[0]['extra']

        pizza_details = db.execute("SELECT id, name, price FROM pizzas WHERE id = ?", pizza_id)
        
        extra_ingredients = db.execute("SELECT * FROM ingredients WHERE id IN (?)", extra_ingredient_ids)
        extraprice = 0
        for price in extra_ingredient_ids:
            pricelist = db.execute("SELECT price FROM ingredients WHERE id = ?", price)
            extraprice = extraprice + pricelist[0]['price']
            
        # this shows how the pizza order is structured without the drink part.        
        pizza_order.append({'pizza': pizza_details, 'extra':extra_ingredients, 'price': extraprice})

    drink_order = []
    for drink_id in session["cart"]["drinks"]:
        drinkdata = db.execute("SELECT id, name, price FROM drinks WHERE id = ?", drink_id)
        drink_order.append(drinkdata)
    
    totalprice = finalprice()

        
    return render_template("cart.html", pizza_order=pizza_order, drink_order=drink_order, totalprice=totalprice)

def finalprice():
    totalprice = 0
    for order in session["cart"]["allpizzaorder"]:
        pizza_id = order[0]['pid']
        extra_ingredient_ids = order[0]['extra']
        # Calculating pizza price.
        pizza_price = db.execute("SELECT price FROM pizzas WHERE id = ?", pizza_id)
        totalprice = totalprice + pizza_price[0]['price']
        # Calculating extra ingred price.
        extra_ingredients = db.execute("SELECT price FROM ingredients WHERE id IN (?)", extra_ingredient_ids)
        extraprice = 0
        for price in extra_ingredient_ids:
            pricelist = db.execute("SELECT price FROM ingredients WHERE id = ?", price)
            extraprice = extraprice + pricelist[0]['price']
            totalprice = totalprice + pricelist[0]['price']
    # Calculating drink ingred price.
    drink_order = []
    for drink_id in session["cart"]["drinks"]:
        drinkdata = db.execute("SELECT price FROM drinks WHERE id = ?", drink_id)
        totalprice = totalprice + drinkdata[0]['price']
        
        
    return round(totalprice, 2)