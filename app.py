from flask import Flask, flash, redirect, render_template, request, session, g
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from werkzeug.exceptions import HTTPException
import os, stripe
stripe.api_key = os.environ['STRIPE_SECRET_KEY']
DATABASE = 'sql.db'
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///sql.db")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def index():
    try:
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    except:
        # not logged in
        username = [{"username":""}]

    return render_template("index.html", username=username[0]['username'])

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            flash("You must provide a username!")
            return render_template("register.html")
        elif not request.form.get("password"):
            flash("You must provide a password!")
            return render_template("register.html")
        elif not request.form.get("confirmation"):
            flash("You must confirm your password!")
            return render_template("register.html")
        
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) == 1:
            flash("Username taken!")
            return render_template("register.html")
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords don't match!")
            return render_template("register.html")

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",request.form.get("username"),generate_password_hash(request.form.get("password")),)
        return redirect("/")
    else:
        return render_template("register.html")
@app.route('/login', methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Enter a username!")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Enter a password!")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username/password!")
            return render_template("login.html")
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/menu", methods=["GET", "POST"])
def menu():
    if request.method == "POST":
        if not session["user_Id"]:
            return redirect("/login")
        
    else:
        products = get_products()
        return render_template("menu.html", products=products)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Successfully logged out!")
    return redirect("/")

def get_products():
    products = db.execute("SELECT * FROM products")
    return products

@app.route('/products/<string:product>', methods=['GET', 'POST'])
def product(product):
  if request.method == "POST":
        product = request.form.get("product")
        quanity = request.form.get("quanity")
        modifiers = request.form.get("modifiers")
        price = request.form.get("price")
        db.execute("INSERT INTO cart (user, product, quanity, modifiers,price) VALUES (?,?,?,?,?)", session["user_id"], product, quanity, modifiers, price)
        return redirect("/cart")
  else:
        product_info = db.execute("SELECT * FROM products WHERE shortname = ?", product)
        return render_template("product.html", product=product_info[0])

@app.route('/cart', methods=["GET", "POST"])
@login_required
def cart():
    if request.method == "POST":
        None
    else:
        cart = db.execute("SELECT * FROM CART WHERE user = ?", session["user_id"])
        return render_template("cart.html", cart=cart)

@app.errorhandler(HTTPException)
def handle_exception(e):
    error_info = {
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }
    return render_template("error.html", error_info=error_info), e.code
if __name__ == '__main__':
   app.run()
