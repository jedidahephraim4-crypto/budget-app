from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

transactions = []
budgets = {}

class Transaction(BaseModel):
    amount:float
    category: str
    type : str

class Budget(BaseModel):
    category : str
    limit : float



@app.get("/")
def home():
    return {"message": "Budget App Backend Running"}

@app.get("/transactions")
def get_transactions():
    return transactions
@app.get("/budgets")
def get_budgets():
    return budgets

@app.post("/transactions")
def add_transaction(transaction: Transaction):
    transaction_data = transaction.dict()
    transaction_data["date"] = datetime.now().strftime("%Y-%m-%d")

    transactions.append(transaction_data)

    return {
        "message": "Transaction added",
        "transaction":transaction_data
    } 


@app.post("/budgets")
def add_budget(budget: Budget):
    budgets[budget.category] = budget.limit

    return {
        "message": "Budget set",
        "budget" : budget
    }


@app.get("/summary")
def get_summary():
    total_income = 0
    total_expenses = 0
    total_savings = 0
    last_updated = None

    for transaction in transactions:
        last_updated = transaction["date"]

        if transaction["type"] == "income":
            total_income += transaction["amount"]

        elif transaction["type"] == "expense":
            total_expenses += transaction["amount"]

        elif transaction["type"] == "savings":
            total_savings += transaction["amount"]
    remaining_balance = total_income - total_expenses - total_savings

    return {
        "total_income" : total_income,
        "total_expenses" : total_expenses,
        "total_savings" : total_savings,
        "remaining_balance" : remaining_balance,
        "last_updated" : last_updated,
        "budgets" : get_budget_status
    }


@app.get("/spending-by-category")
def get_spending_by_category():
    category_totals = {}

    for transaction in transactions:
        if transaction.type == "expense":
            category = transaction.category
            amount = transaction.amount

            if category in category_totals:
                category_totals[category] += amount

            else:
                category_totals[category] = amount
    return category_totals
@app.get("/budget-status")
def get_budget_status():
    spending_by_category = {}


    for transaction in transactions:
        if transaction["type"] == "expense":
            category = transaction["category"]
            amount = transaction["amount"]
            
            if catergory in spending_by_category:
                spending_by_category += amount
            
            else:
                spending_by_category = amount

    budget_status = {}

    for category in budgets:
        limit = budgets[category]
        spent = spending_by_category.get(category,0)
        remaining = limit - spent

        budget_status[category] = {
            "budget" : limit,
            "spend" : spent,
            "remaning" : remaining,
            "over_budget" : spent > limit
        }
    return budget_status