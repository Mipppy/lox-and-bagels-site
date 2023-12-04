from flask import Flask, flash, redirect, render_template, request, session, g
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import HTTPException
from flask_mail import Mail, Message
from helpers import *
import os, stripe, random, string
stripe.api_key = os.environ['STRIPE_SECRET_KEY']
DATABASE = 'sql.db'
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'loxofbagelsandmoor@gmail.com'
app.config['MAIL_PASSWORD'] = 'glfp hkkk hbqw fkbe'
app.config['MAIL_DEFAULT_SENDER'] = 'confirmation@loxofbagelsandmoor.com'
Session(app)
mail = Mail(app)
db = SQL("sqlite:///sql.db")

app.jinja_env.filters["usd"] = usd

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
        username = db.execute("SELECT firstname,lastname FROM users WHERE id = ?", session["user_id"])
        username = username[0]['firstname'] + " " + username[0]['lastname']
    except:
        # not logged in
        username = ""

    return render_template("index.html", username=username)

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
        elif not request.form.get("firstname"):
            flash("Enter your first name!")
            return render_template('register.html')
        elif not request.form.get('lastname'):
            flash("Enter your last name!")
            return render_template("register.html")
        elif not request.form.get("email"):
            flash("Enter an email address!")
            return render_template("register.html")    
        
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) == 1:
            flash("Username taken!")
            return render_template("register.html")
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords don't match!")
            return render_template("register.html")
        
        verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        session['verification_data'] = {'email': request.form.get("email"), 'code': verification_code, 'firstname': request.form.get("firstname"), 'username': request.form.get("username"), 'lastname': request.form.get("lastname"), 'password': request.form.get("password")}
        send_email(request.form.get("email"), "Verification Code", verification_code)
        # db.execute("INSERT INTO users (username, hash, firstname, lastname) VALUES (?, ?, ?, ?)",request.form.get("username"),generate_password_hash(request.form.get("password")), request.form.get("firstname"), request.form.get("lastname"))
        return redirect("/verify")
    else:
        return render_template("register.html")
    
@app.route('/verify', methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        if not request.form.get("code"):
            flash("Enter a code!")
            return render_template("verify.html")
        if request.form.get("code") == session['verification_data']['code']:
            db.execute("INSERT INTO users (username, hash, firstname, lastname, email) VALUES (?, ?, ?, ?, ?)",session['verification_data']['username'],generate_password_hash(session['verification_data']['password']), session['verification_data']['firstname'], session['verification_data']['lastname'], session['verification_data']['email']) 
            return redirect("/login")
        else:
            flash("Code does not match")
            return render_template('verify.html')
    else:
        return render_template("verify.html")

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
    cart = db.execute("SELECT * FROM CART WHERE user = ?", session["user_id"])
    if request.method == "POST":
        price_total = 0
        for index in cart:
            price_total += (index['price'] * index['quanity'])
        stripe_payment_processing = stripe.checkout.Session.create(
            line_items = [
                {
                    'price_data': {
                        'product_data': {
                            'name': 'Lox of Bagels Order'
                        },
                        'unit_amount': price_total,
                        'currency': 'usd',
                    },
                    'quantity' : 1,
                }
            ],
            payment_method_types=['card'],
            mode='payment',
            success_url=request.host_url + 'order?success=true',
            cancel_url=request.host_url + 'order?success=',
        )
        return redirect(stripe_payment_processing.url)
    else:
        return render_template("cart.html", cart=cart)

@app.route('/order', methods=["GET"])
@login_required
def order():
    success = request.args.get('success', default=False)
    if success:
        db.execute("DELETE FROM cart WHERE user = ?", session["user_id"])
    return render_template("order.html", success=success)

@app.route('/history', methods=["GET", "POST"])
@login_required
def history():
    if request.method == "POST":
        None
    else:
        return render_template("history.html")

@app.errorhandler(HTTPException)
def handle_exception(e):
    error_info = {
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }
    return render_template("error.html", error_info=error_info), e.code

def send_email(to, subject,code):
    msg = Message(
        subject,
        recipients=[to],
        html=f'<p>Your code is: </p> <br> <h1>{code}</h1>',
        sender="confirmation@loxofbagelsandmoor.com",
    )
    mail.send(msg)

@app.route('/removefromcart', methods=["POST"])
def remove_from_cart():
    product = request.form.get("productid")
    db.execute("DELETE FROM cart WHERE user = ? AND product = ?", session["user_id"], product)
    flash("Successfully removed from cart")
    return redirect("/cart")


if __name__ == '__main__':
   app.run()
