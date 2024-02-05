# PizzaTime
#### Video Demo:  <URL HERE>
#### Description:
PizzaTime is a Flask based webapp which allows the user to register to the page, log in, add pizzas to the cart, select extra ingredients for each pizza, add drinks to the cart, finalise order and submit a form, monitor order status  live, without refreshing the page. 
From an admin side, the webapp allows the admin to change a user's role to admin, monitor the incoming orders, change the order details including the status.

## Files and their function in this project.

### Instance folder
Since the project uses Flask-admin too, the database must be placed in the instance folder so that the admin page can recongnise it. The databese has 5 main tables:  
  
Users table - this table contains the registered user details and whther a user is and admin or not.  
Pizzas table - since, this it pizza ordering webapp, a pizzas table was created to store the pizza related details, e.g. name, price, route, img.  
Ingredients table - this table holds the extra ingredients that can be picked for each pizza.  
Drinks table - this table hold the drink-related details, similarly to pizzas table.  
Myorder table - the orders are stored in this table.  

### Static folder
Within the static folder there are three main files.  
 
#### Images (credit)
The images file stores all the related images that are rendered when the webapp is running. 

Images used in this project are sourced from [Pizza Monkey](https://szeged.pizzamonkey.hu/termekek/pizzak/normal-pizzak/#/). The images are the property of Pizza Monkey and are used solely for CS50Final Project.

For more information and to view the original images, please visit [Pizza Monkey](https://szeged.pizzamonkey.hu/termekek/pizzak/normal-pizzak/#/).  

#### Javascript
The javascript.js file contains the javascript for the AJAX. When the admin changes the order status of a pizza order, the execution of the content of the js file is called in each 5 seconds if the user stays on /myorder. The script changes the order status on each card and also updates the bootstrap color code of each card.
#### CSS
The styles.ccs file is responsible for the behaviour of the footer. It keeps it at the bottom of the page even if the body is empty.

### Templates folder

This folder contains all the templates that are used in this project. There is a layout.html file upon which all the other templates are built. Each template is dynamically populated with Jinja.  
For the design, Bootstrap was used.

### Requriements

The required libraries are stored in the requriements.txt file.

## app.py
This file is responsible for the operation of the webapp. After the flask app is configured, and error handler function is defined that can be called if the user does not provide a valid URL.  
  
With the help of jinja, the "/" route lists all the pizzas that can be bought.  
  
The register, login and logout routes are built on the logic that was used in the Finance problem set. However, if the user does not provide the login details correctly, a flash message is sent instead of the grumpy cat.
  
/myorder returns the orders that are stored in the database based on the user that is logged in.  

/myorderdata is responsible for serving the AJAX requests with fresh data.  

/drinks lists all the drinks in a similar manner how / operates.  

/cart is a difficult route. It fetches the content of the form that is sent for pizza orders. Cart is actually a session and the session looks like this: session["cart"] = {"allpizzaorder": [], "drinks": []}.  
drink is a list of integers and allpizzaorder is a list that contains lists of dicts. You can depict allpizzaorder like this: allpizzaorder[[{'pid' : pizzaid, 'extra': chosen_extra_ingredients}]]. This way when the user picks extra ingredients for a specific pizza, they are stored together.  
The process_cart() function is called at the end which uses the values in the session to look for the particular item details in the database and render it on the cart page.  

/order is responsible for collecting the order details and based on the content of the cart session sql queries are made to get the details of the ordered items and store them as a string in the order table. In order to simplify the app, one order is stored in as one row in the databe, thus in case of multiple pizza orders with multiple extra ingredients, the details are stored in one cell as a string e.g. Jalapeno - Spinach, Basil, Cherry Tomatoes; Bacon - Olives, Basil.  

/cancelorder allows the user to cancel an order if the status is "Order received". There are server side checks implemented not to allow a user to cancel an order for other status. Thus the user cannot change the status of delivered pizza back to in progress. 

/<pizza_route> is a dinamic route for generating pizza routes. The routes are stored in the pizza table, thus if the user tries to access a non existing route, a 404 error page is rendered.  

It is also important to note that I came accross an issue that I could not fully resolve. I noteced that if I hit the browsers back button after I'm redirected to the /myorder page after an order, the cart is not being cleared, since the whole cart page is cached and no GET request is sent to the server. I could only implement a hard refresh with javascript and implement token system not to submit the previous order to the cart again by refreshing the page. The issue here is that if I don't apply caching like in the case of Finance, and the user hits the back button, then the user receives a cache error from the browser. Thus, I could not get the browser to load freshly even with javascript if the caching was turned off.

## helpers.py
The login_required and usd function was borrowed from the Finance problem set.  
The process_cart function takes the ids stored in the cart session and queries them in order to get the item details form the database and render the html template with the details.  
The finalprice function calculates the total cost of the order similarly how the process_cart function utilises the cart session.









