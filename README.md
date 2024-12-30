# EaseMyBudget
### Video Demo:  [<URL HERE>](https://youtu.be/wQQvlN2yxug)
## Description:
EaseMyBudget is a web-app developed with combination of Python, Sqlite3, Flask framework, HTML, CSS and JavaScript. As an undergrad student I have hard time keeping track of my expenses and income. With the help of CS50 course, I developed this app to keep track of expenses. 
>It helps you understand your spending habits, identify areas where you can cut back, set financial goals, and ultimately make informed decisions about your money by providing a clear picture of where your income is going across different categories of expenses.
>
#### Some features of my web-app:
* Add and categorize your expenses easily.
* Review income and expenses on a weekly, monthly, or half-yearly basis.
* The dashboard displays cards summarizing expenses and income for each category.
* A radar chart highlights your highest spending areas.
* Compare your spending across different time periods using the histogram.
* View all transactions in chronological order, from newest to oldest.

## Walkthrough
The project is divided into multiple files and sub directories.
* app.py - handles https request, form validation, process data and render templates.
* helper.py - It contains different fuctions to help app.y fetch data from database, process it and finally return it.
* /static - holds all the .png, .csv and .js files
* /templates - contains the necessary .html structure.
* requirements.txt - contains list of packages and libraries required by the project.

When you visit the webpage, you'll be redirected to the login page (if you're not logged in already).
### app.py
```py
@login_required # ensures that the user is logged in to view the page.
```
```py
@app.route("/register", methods=["GET", "POST"])
def register():
```
The register function returns the register.html template on GET request.
On POST request mulitple validations are performed to remove any discrepancy.
The user name is checked for unqiueness, ensuring no two users can have the same username.
The password is hashed before writing to db using `generate_password_hash()` fn. This ensure that the password is stored securely.
```py
if username and password and (password == confirmation):
    try:
        db.execute("INSERT INTO users (username, password) VALUES (?,?)",
                   username, generate_password_hash(password))
    except ValueError:
        return apology("Username already exists.")
    return redirect("/login")
else:
    return apology("Either input is blank or the passwords do not match.")
```

```py
@app.route("/login", methods=["GET", "POST"])
def login():
```
The login function returns the login.html page on GET request. Upon form submition of form through POST request, user name and password are validated,
on failure 403 error is returned.
```py
# Ensure username was submitted
if not request.form.get("username"):
    return apology("must provide username", 403)

# Ensure password was submitted
if not request.form.get("password"):
    return apology("must provide password", 403)
```
Upon validation the password matching is done by reteriving the username and hashed password from db,
if success user session is saved using browser cookies, the user login is redirected to dashboard and a flash message is displayed,
otherwise 403 error is displayed.
```py
rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
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
```
```py
@app.route("/expense", methods=["GET", "POST"])
@login_required
def expense():
    """Show expense form"""
    ...
    return render_template("income.html")
      
```
Expense function renders the expenese.html form upon recieving GET request.
On POST request the data is validated. 
The description must be non empty, amount must be numeric and category must be a valid one.
```py
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
```
If the data is accepted, it writes to db and returns the user to dashboard along with a flash message.
Income function is similar to expense function, the only key difference is that it writes to income table instead.
```py
@app.route("/income", methods=["GET", "POST"])
@login_required
def income():
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
```
The index function is responsible for homepage view, it calls various functions from helper.py and the fetched data is passed to html template.
```py
@app.route("/")
@login_required
def index():
    """Show Dashboard"""
``` 
The get_expense function returns a dictionary of data. It takes the id and no of days as argument and returns the desired range of data.
```py
weekly_expense = get_expense(id, 7)
monthly_expense = get_expense(id, 30)
halfyearly_expense = get_expense(id, 180)
```
Similarly get_income function returns a dictoinary of data according to passed parameter.(More details in helper.py)
```py
weekly_income = get_income(id,7)
monthly_income = get_income(id,30)
halfyearly_income= get_income(id, 180)
```
The get_transaction statement merges the expenses and income table ordered by date time and returns it.
```py
weekly_transaction_statment = get_transaction_statment(weekly_expense["expense_list"], weekly_income["income_list"])
monthly_transaction_statment = get_transaction_statment(monthly_expense["expense_list"], monthly_income["income_list"])
halfyearly_transaction_statment = get_transaction_statment(halfyearly_expense["expense_list"], halfyearly_income["income_list"])
```
Finally the data is retunred to index.html and displayed with the help of jinja template engine.
### helper.py
The helper.py contains functions, that supports the functions in app.py.
#### login_required
Checks whether the user id exists if not it redirects the user to login page.
#### apology
Takes a message and error code (default 400) and renders a apology page when something goes wrong.
```py
return render_template("apology.html", err=code, message=msg), code
```
#### get_expense
The get expense function runs multiple SQL SELECT queries, process the data and returns the data in the form of dictoinary.
It takes two arguments first one being id and second one being search range.
Depending on the search range it runs the required set of queries and statements.
At last a dictionary is returned.
#### get_income 
Similar to get_expense function.
#### get_transaction_statement
Takes expense and income list and combines them ordered by date time and returns an ordered dictionary.
### inr
Jinja filter that formats the amount to INDIAN RUPEE. In future could be modified to support multiple currencies.
```py
return date.fromisoformat(value).strftime("%a, %d %b %y")
```
### layout.html
Holds the base html structure containing header and footer. Used in sub page by extends feature.
### /statics
Holds the neccessay css and js files.
### HTML
The forntend is implemented with Boostrap 5 allowing all sorts of customizations and styles.
For charts chart.js has been used.
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```
