from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

transactions = []

class Transaction(BaseModel):
    amount:float
    category: str
    type : str


@app.get("/")
def home():
    return {"message": "Budget App Backend Running"}

@app.get("/transactions")
def get_transactions():
    return transactions

@app.post("/transactions")
def add_transaction(transaction: Transaction):
    transactions.append(transaction)
    return {
        "message": "Transaction added",
        "transaction":transaction
    } 
@app.get("/summary")
def get_summary():
    total_income = 0
    total_expenses = 0

    for transaction in transactions:
        if transaction.type == "income":
            total_income += transaction.amount
        elif transaction.type == "expense":
            total_expenses += transaction.amount
    remaining_balance = total_income - total_expenses

    return{
        "total_income" : total_income,
        "total_expenses" : total_expenses,
        "remaining_balance" : remaining_balance
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