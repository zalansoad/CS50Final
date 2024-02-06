# PizzaTime
#### Video Demo:  <URL HERE>
#### Description:
PizzaTime is a Flask-based web app which allows the user to register to the page, log in, add pizzas to the cart, select extra ingredients for each pizza, add drinks to the cart, finalise order, and monitor order status live without refreshing the page. 
From an admin side, the web app allows the admin to change a user's role to admin, monitor the incoming orders, change the order details including the status.

# Table of Contents

1. [Files and their Function](#files-and-their-function)
   1.1. [Instance Folder](#instance-folder)
   1.2. [Static Folder](#static-folder)
      1.2.1. [Images (credit)](#images-credit)
      1.2.2. [JavaScript](#javascript)
      1.2.3. [CSS](#css)
   1.3. [Templates Folder](#templates-folder)
   1.4. [Requirements](#requirements)
2. [The main Python file: app.py](#the-main-python-file-apppy)
3. [The helper Python file: helpers.py](#the-helper-python-file-helperspy)


## Files and their function.

### Instance folder
Since the project uses Flask-Admin too, the database must be placed in the instance folder so that Flask-Admin can recognise it. The database has 5 main tables:  
  
**Users table** - this table contains the registered user details e.g. username, password, user type (user/admin).  
**Pizzas table** - since, this is a pizza ordering web app, the pizzas table was created in order to store the pizza related details, e.g. name, price, route, img.  
**Ingredients table** - this table stores the extra ingredients that can be picked for each pizza.  
**Drinks table** - this table stores the drink-related details, similarly to pizzas table.  
**Myorder table** - the orders are stored in this table.  

### Static folder
Within the static folder, there are three main files.  
 
#### Images (credit)
The images file stores all the related images that are rendered when the web app is running. 

Images used in this project are sourced from [Pizza Monkey](https://szeged.pizzamonkey.hu/termekek/pizzak/normal-pizzak/#/). The images are the property of Pizza Monkey and are used solely for CS50 Final Project.

For more information and to view the original images, please visit [Pizza Monkey](https://szeged.pizzamonkey.hu/termekek/pizzak/normal-pizzak/#/).  

#### JavaScript
The **javascript.js** file contains the JavaScript for the AJAX. When an admin changes the order status of a pizza order, the execution of the content of the js file is called in each 5 seconds if the user stays on the /myorder page. The script changes the order status on each card and also updates the bootstrap color code of each card.

#### CSS
The **styles.ccs** file is responsible for the behaviour of the footer. It keeps it at the bottom of the page even if the body is empty.

### Templates folder
This folder contains all the templates that are used in this project. There is a layout.html file upon which all the other templates are built. Each template is dynamically populated with Jinja.  
For the design, Bootstrap 5.3.2. was used along with its JavaScript features.

### Requirements
The required Python libraries are stored in the requirements.txt file.

## The main Python file: app.py
This file is responsible for the operation of the web app. After the Flask app is configured, the error handler function is defined that can be called if the user does not provide a valid URL. This builds upon the fact that some routes are generated dynamically  

Since the web app uses Flask-Admin too, the use of SQLALCHEMY and the creation of models and model views were inevitable.
  
With the help of jinja, the **"/"** route lists all the pizzas that can be bought.  
  
The **register, login, and logout routes** are built on the logic that was used in the Finance problem set. However, if the user does not provide the login details correctly, a flash message is sent instead of the grumpy cat.
  
**/myorder** returns the orders that are stored in the database in accordance to the user that is logged in. In these SQL queries cs50 SQL library was used.   

**/myorderdata** is responsible for serving the AJAX requests with fresh data.  

**/drinks** lists all the drinks in a similar manner how "/" operates.  

**/cart** is a more complex route. It fetches the content of the forms that are sent from the individual pizza pages. Cart is actually a session and the session is built up like this: session["cart"] = {"allpizzaorder": [], "drinks": []}.  
Drinks is a list of integers and allpizzaorder is a list that contains lists of dictionaries. You can depict allpizzaorder like this: allpizzaorder[[{'pid' : pizzaid, 'extra': chosen_extra_ingredients}]]. This way when the user picks extra ingredients for a specific pizza, they are stored together.  
The process_cart() function is called at the end which uses the values in the session to look for the particular item details in the database and render them on the cart page.  

**/order** is responsible for collecting the order details and based on the content of the cart session, SQL queries are made to get the details of the ordered items and store them as a string in the order table. In order to simplify the app, one order is stored in one row in the database, thus, in the case of multiple pizza orders with multiple extra ingredients, the details are stored in one cell as a string, for example, like this: Jalapeno - Spinach, Basil, Cherry Tomatoes; Bacon - Olives, Basil.  

**/cancelorder** allows the user to cancel an order if the status is "Order received". There are server side validations implemented not to allow a user to cancel an order for other status. Thus, the user cannot change the status of delivered pizza orders back to in progress.  

**/<pizza_route>** is a dynamic route for generating pizza routes. The routes are stored in the pizza table, thus if the user tries to access a non-existing route, a 404 error page is rendered.  

It is also important to note that I came across with an issue for which I could not resolve the root cause, but I managed to handle it in a user friendly way. I noticed that if I hit the back button of the browser after being redirected to the /myorder page after a successful order, the cart is not being cleared, since the whole cart page is cached and no GET request is sent to the server. From the server side, the cart is empty, and if one clicks on the cart menu button, the cart indeed shows nothing. I could only implement hard refresh with JavaScript and I also implement token system not to submit the previous order to the cart again by refreshing the page. Another issue here is that if I don't apply caching like in the case of Finance, and the user hits the back button, then the user receives a cache error from the browser. Thus, I could not get the browser to load freshly even with JavaScript if the caching was turned off.

## The helper Python file: helpers.py
The **login_required and usd function** was borrowed from the Finance problem set.  
The process_cart function takes the ids that are stored in the cart session and queries them in order to get the item details form the database and render the html template with these queried details.  
The **finalprice** function calculates the total cost of the order similarly how the process_cart function utilises the cart session.