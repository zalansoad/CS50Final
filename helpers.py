from functools import wraps
from flask import render_template

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

def error_message(message, code=400):
    return render_template("apology.html", message=message, code=code)