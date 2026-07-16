from fastapi import FastAPI, Depends
from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import Literal
import json
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TransactionModel(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    amount = Column(Float)
    category = Column(String)
    type = Column(String)
    date = Column(String)

class BudgetModel(Base):
    __tablename__ = "budgets"
    category = Column(String, primary_key=True)
    limit = Column(Float)

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173","http://localhost:5176","http://localhost:5177","http://localhost:5178","http://localhost:5179"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
class Transaction(BaseModel):
    amount: float
    category: str
    type: Literal["income", "expense", "savings"]

class Budget(BaseModel):
    category: str
    limit: float


@app.get("/")
def home():
    return {"message": "Budget App Backend Running"}

@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    transactions= db.query(TransactionModel).all()
    return [{"id": t.id, "amount": t.amount, "category":t.category, "type":t.type, "date":t.date} for t in transactions]

@app.get("/budgets")
def get_budgets(db: Session = Depends(get_db)):
    budgets = db.query(BudgetModel).all()
    return {b.category: b.limit for b in budgets}


@app.post("/transactions")
def add_transaction(transaction: Transaction, db: Session = Depends(get_db)):
    new_transaction = TransactionModel(
        id=str(uuid.uuid4()),
        amount=transaction.amount,
        category=transaction.category,
        type=transaction.type,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return {"message": "Transaction added", "transaction": {"id": new_transaction.id, "amount": new_transaction.amount, "category": new_transaction.category, "type": new_transaction.type, "date": new_transaction.date}}


@app.post("/budgets")
def add_budget(budget: Budget, db: Session = Depends(get_db)):
    exisiting = db.query(BudgetModel).filter(BudgetModel.category == budget.category).first()
    if exisiting:
        exisiting.limit = budget.limit
    else:
        new_budget = BudgetModel(category=budget.category, limit=budget.limit)
        db.add(new_budget)
    db.commit()
    return{"message" : "Budget set", "budget": budget}



@app.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    transactions = db.query(TransactionModel).all()
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expenses = sum(t.amount for t in transactions if t.type == "expense")
    total_savings = sum(t.amount for t in transactions if t.type == "savings")
    remaining_balance = total_income - total_expenses - total_savings
    last_updated = transactions[-1].date if transactions else None
    return {
        "total_income" : total_income,
        "total_expenses" : total_expenses,
        "total_savings" : total_savings,
        "remaining_balance" : remaining_balance,
        "last_updated" : last_updated,
        "budgets" : get_budget_status(db)
    }




@app.get("/spending-by-category")
def get_spending_by_category(db: Session = Depends(get_db)):
    transactions = db.query(TransactionModel).filter(TransactionModel.type == "expense").all()
    category_totals = {}

    for t in transactions:
        category_totals[t.category] = category_totals.get(t.category,0) + t.amount
    return category_totals




@app.get("/budget-status")
def get_budget_status(db: Session = Depends(get_db)):
    transactions = db.query(TransactionModel).filter(TransactionModel.type == "expense").all()
    spending = {}


    for t in transactions:
        spending[t.category] = spending.get(t.category,0) + t.amount
        budgets = db.query(BudgetModel).all()
    return {
        b.category: {
            "budget": b.limit,
            "spent": spending.get(b.category,0),
            "remaining": b.limit - spending.get(b.category,0),
            "over_budget" : spending.get(b.category, 0) > b.limit
        }
        for b in budgets
    }
@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id:str, db: Session = Depends(get_db)):
    transaction = db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
    if transaction:
        db.delete(transaction)
        db.commit()
        return{"message": "Transaction removed"}
    return{"message" : "Transaction not found"}

@app.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: str, updated_transaction: Transaction, db: Session = Depends(get_db)):
    transaction = db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
    if transaction:
        transaction.amount = updated_transaction.amount
        transaction.category = updated_transaction.category
        transaction.type = updated_transaction.type
        transaction.date = datetime.now().strftime("%Y-%m-%d")
        db.commit()
        db.refresh(transaction)
        return{"message": "Transaction updated", "transaction": {"id": transaction.id, "amount": transaction.amount, "category": transaction.category, "type": transaction.type, "date":transaction.date}}
    return {"message": "Transaction not found"}

    