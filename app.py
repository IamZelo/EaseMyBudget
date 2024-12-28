import os
import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology, get_expense, get_income, get_transaction_statment, inr, format_date

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["inr"] = inr
app.jinja_env.filters["formatDate"] = format_date


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///easebudget.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], request.form.get("password")
        ):
            return apology("invalid username / password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash(f"Logged in as {rows[0]["username"]}")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if username and password and (password == confirmation):
            try:
                db.execute("INSERT INTO users (username, password) VALUES (?,?)",
                           username, generate_password_hash(password))
            except ValueError:
                return apology("Username already exists.")
            return redirect("/login")
        else:
            return apology("Either input is blank or the passwords do not match.")

    return render_template("register.html")


@app.route("/")
@login_required
def index():
    """Show Dashboard"""
    id = session["user_id"]
    weekly_expense = get_expense(id, 7)
    monthly_expense = get_expense(id, 30)
    halfyearly_expense = get_expense(id, 180)
    
    weekly_income = get_income(id,7)
    monthly_income = get_income(id,30)
    halfyearly_income= get_income(id, 180)

    weekly_transaction_statment = get_transaction_statment(weekly_expense["expense_list"], weekly_income["income_list"])
    monthly_transaction_statment = get_transaction_statment(monthly_expense["expense_list"], monthly_income["income_list"])
    halfyearly_transaction_statment = get_transaction_statment(halfyearly_expense["expense_list"], halfyearly_income["income_list"])
    return render_template("index.html", weekly_transaction_statment=weekly_transaction_statment,
                           monthly_transaction_statment=monthly_transaction_statment,
                           halfyearly_transaction_statment=halfyearly_transaction_statment,
                           weekly = weekly_expense|weekly_income,
                           monthly = monthly_expense|monthly_income,
                           halfyearly=halfyearly_expense|halfyearly_income)


@app.route("/expense", methods=["GET", "POST"])
@login_required
def expense():
    """Show expense form"""
    
    categories = []
    for item in db.execute("SELECT category FROM categories"):
        categories.append(item['category'])
    
    if request.method == "POST":
        id  = session["user_id"]
        description = request.form.get("description")
        amount = request.form.get("amount")
        category = request.form.get("category")
        
        # Perform input validation
        if not description:
            return apology("Please enter description")
        try:
            amount = amount.replace(",", "")
            amount = float(amount)
        except ValueError:
            return apology("Amount must be Numeric only")
        
        if amount < 0:
            return apology("Amount must be non negative!")
        if category not in categories:
            return apology("Invalid category")
        
        db.execute("INSERT INTO expenses (user_id, description, category, amount) VALUES (?,?,?,?)", id, description, category, amount)
        flash("Expense added!")
        return redirect("/")
    
    return render_template("expense.html", categories = categories)

@app.route("/income", methods=["GET", "POST"])
@login_required
def income():
    """Show income form"""
    if request.method == "POST":
        id  = session["user_id"]
        description = request.form.get("description")
        amount = request.form.get("amount")
        
        # Perform input validation
        if not description:
            return apology("Please enter description")
        if not amount.isnumeric():
            return apology("Amount must be Numeric only")
        amount = float(amount)
        if amount < 0:
            return apology("Amount must be non negative!")
        
        db.execute("INSERT INTO income (user_id, description, amount) VALUES (?,?,?)", id, description, amount)
        flash("Income added!")
        return redirect("/")
    
    return render_template("income.html")