import datetime
from operator import itemgetter
from flask import redirect, session, render_template
from functools import wraps
from cs50 import SQL
from datetime import date

import locale
locale.setlocale(locale.LC_MONETARY, 'en_IN')

db = SQL("sqlite:///easebudget.db")


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def apology(msg, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", err=code, message=msg), code

def get_expense(id,day):
    """Returns expense of a particular user."""
    category_expense = db.execute(
        f"SELECT category, SUM(amount) AS 'amount' FROM expenses WHERE user_id = ? AND DATE(date_time) > DATE(DATE(), '-{day} day') GROUP BY category ORDER BY amount DESC", id)
    category = db.execute("SELECT category FROM categories")
    category = [x['category'] for x in category]
    for item in category_expense:
        category.remove(item['category'])
    for item in category:
            category_expense.append({'category':item, 'amount':0})
    
    expense_list = db.execute(f"""SELECT date_time, DATE(date_time) as date, description, category, amount
                                    FROM expenses 
                                    WHERE user_id = ? AND DATE(date_time) > DATE(DATE(), '-{day} day') 
                                    ORDER BY date_time DESC""", id)
    
    expense_sum = 0
    for item in expense_list:
        expense_sum += item["amount"]
    
    expense_history_day = []
    expense_history_amt = []
    # Get history for the week
    if day == 7:
        expense_history = db.execute(f"""SELECT CASE CAST (STRFTIME('%w',date_time) AS INTEGER) when 0 then 'Sun'
                                            when 1 then 'Mon'
                                            when 2 then 'Tue'
                                            when 3 then 'Wed'
                                            when 4 then 'Thu'
                                            when 5 then 'Fri'
                                            else 'Sat' end as weekday, SUM(amount) AS amount 
                                            FROM expenses 
                                            WHERE user_id = ? AND DATE(date_time) > DATE(DATE(), '-{day} day') 
                                            GROUP BY DATE(date_time)
                                            ORDER BY DATE(date_time)""", id)
        
        day_dic= {'Sun':0,'Mon':1, 'Tue':2, 'Wed':3, 'Thu':4, 'Fri':5, 'Sat':6}
        for item in expense_history:
           day_dic.pop(item['weekday'])
        for item in day_dic:
            expense_history.insert(day_dic[item],{'weekday':item, 'amount':0})
        
        for item in expense_history:
            expense_history_day.append(item['weekday'])
            expense_history_amt.append(item['amount'])
    elif day == 30:
        expense_history = db.execute(f"""SELECT STRFTIME('%d/%m',date_time) as date, STRFTIME('%Y%m%d', date_time) as cmpdate, SUM(amount) AS amount
                                     FROM expenses WHERE user_id = ? AND DATE(date_time) > DATE(DATE(), '-{day} day') 
                                     GROUP BY DATE(date_time) 
                                     ORDER BY date_time;""", id)
        num_of_dates = day
        start = datetime.datetime.today()
        date_list = [(start.date() - datetime.timedelta(days=x)).strftime("%Y%m%d") for x in range(num_of_dates)]
        for item in expense_history:
            date_list.remove(item['cmpdate'])
        for item in date_list:
            expense_history.append({'date':item[6:]+'/'+ item[4:6], "cmpdate":item, 'amount':0})
        sorted_expense_history = sorted(expense_history, key=itemgetter('cmpdate'))
            
        for item in sorted_expense_history:
            expense_history_day.append(item['date'])
            expense_history_amt.append(item['amount'])

    
    # day_dic= {'Sun':0,'Mon':1, 'Tue':2, 'Wed':3, 'Thu':4, 'Fri':5, 'Sat':6}
    # for item in expense_history:
    #     day_dic.pop(item['weekday'])
    # for item in day_dic:
    #     expense_history.insert(day_dic[item],{'weekday':item, 'amount':0})
    # expense_dict = {}
    # for item in expense_list:
    #     if item["date"] in expense_dict:
    #         expense_dict[item["date"]].append(item)
    #     else:
    #         expense_dict[item["date"]]= [item,]
    elif day == 180:
        expense_history = db.execute(f"""SELECT STRFTIME('%m',date_time) as month, SUM(amount) AS amount
                                        FROM expenses WHERE user_id = ? AND DATE(date_time) > DATE(DATE(), '-{day} day') 
                                        GROUP BY month
                                        ORDER BY month;""", id)
        if expense_history:
            month_dict = {1:'Jan', 2:'Feb', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 1:'Dec'}
            month_dict_new = month_dict.copy()
            for item in expense_history:
                month_dict_new.pop(int(item['month']))
            
            delta_month = int(expense_history[-1]['month'])- 6
            if delta_month < 0:
                delta_month += 12
                
            for item in expense_history:
                item['month'] = month_dict[int(item['month'])]
                
            temp = []
            for item in month_dict_new:
                if item >= delta_month:
                    temp.append({'month':month_dict_new[item], 'amount':0})
            temp.extend(expense_history)
            sorted_expense_history = temp
            
            for item in sorted_expense_history:
                expense_history_day.append(item['month'])
                expense_history_amt.append(item['amount'])
        
    category_lst = []
    category_amt = []
    for item in category_expense:
        category_lst.append(item['category'])
        category_amt.append(item['amount'])
        
    return {"expense_list":expense_list, "expense_sum":expense_sum, "category_expense":category_expense, "category_lst":category_lst, "category_amt":category_amt, "expense_history_day":expense_history_day, "expense_history_amt":expense_history_amt}

def get_income(id,day):
    income_list = db.execute(f"""SELECT date_time, DATE(date_time) as date, description, category, amount
                                    FROM income 
                                    WHERE user_id = ? AND DATE(date_time) > DATE(DATE(), '-{day} day') 
                                    ORDER BY date_time DESC""", id)
    income_sum = 0
    for item in income_list:
        income_sum += item["amount"]
    return{"income_list":income_list, "income_sum":income_sum}


def get_transaction_statment(expense_list, income_list):
    transaction_statment = []
    transaction_statment.extend(expense_list)
    transaction_statment.extend(income_list)
    sorted_transaction_statement = sorted(transaction_statment, key=lambda x: x['date_time'], reverse=True)
    
    for item in sorted_transaction_statement:
        if item["category"] != "Income":
            item["amount"] =  -item["amount"]
    
    transaction_statment_dict = {} 
    for item in sorted_transaction_statement:
        if item["date"] in transaction_statment_dict:
            transaction_statment_dict[item["date"]].append(item)
        else:
            transaction_statment_dict[item["date"]]= [item,]
    return transaction_statment_dict
    

def inr(value):
    """Format value as INR."""
    if value < 0:
        value = abs(value)
        return "-  "+ locale.currency(value, grouping=True)
        
    return locale.currency(value, grouping=True)

def format_date(value):
    """Format date"""
    return date.fromisoformat(value).strftime("%a, %d %b %y")
