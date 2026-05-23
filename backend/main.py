from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import Literal
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5175"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

transactions = []
budgets = {}
DATA_FILE = "data.json"

def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump({
            "transactions" : transactions,
            "budgets" : budgets
        }, file, indent=4)


def load_data():
    global transactions, budgets

    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            transactions = data.get("transactions", [])
            budgets = data.get("budgets", {})
    except FileNotFoundError:
        transactions = []
        budgets = {}
load_data()

    

class Transaction(BaseModel):
    amount:float
    category: str
    type: Literal["income","expense","savings"]

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
    transaction_data["id"] = str(uuid.uuid4())
    transaction_data["date"] = datetime.now().strftime("%Y-%m-%d")

    transactions.append(transaction_data)
    save_data()

    return {
        "message": "Transaction added",
        "transaction":transaction_data
    } 


@app.post("/budgets")
def add_budget(budget: Budget):
    budgets[budget.category] = budget.limit
    save_data()

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
        "budgets" : get_budget_status()
    }




@app.get("/spending-by-category")
def get_spending_by_category():
    category_totals = {}

    for transaction in transactions:
        if transaction["type"] == "expense":
            category = transaction["category"]
            amount = transaction["amount"]

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
            
            if category in spending_by_category:
                spending_by_category[category] += amount
            
            else:
                spending_by_category[category] = amount

    budget_status = {}

    for category in budgets:
        limit = budgets[category]
        spent = spending_by_category.get(category,0)
        remaining = limit - spent

        budget_status[category] = {
            "budget" : limit,
            "spent" : spent,
            "remaining" : remaining,
            "over_budget" : spent > limit
        }
    return budget_status

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id:str):
    for transaction in transactions:
        if transaction["id"] == transaction_id:
            transactions.remove(transaction)
            save_data()
            return{"message": "Transaction removed"}
    return{"message": "Transaction not found"}

@app.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: str, updated_transaction: Transaction):
    for transaction in transactions:
        if transaction["id"] == transaction_id:
            transaction["amount"] = updated_transaction.amount
            transaction["category"] = updated_transaction.category
            transaction["type"] = updated_transaction.type
            transaction["date"] = datetime.now().strftime("%Y-%m-%d")
            save_data()
            return{
                "message" : "Transaction updated",
                "transaction" : transaction
            }
    return{"message": "Tranasaction not found"}
    