from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
                    "http://127.0.0.1:5500",
                    "https://project-bank-fastapi.vercel.app/"
                  ],
    allow_methods=["*"],
    allow_headers=["*"],
)


accounts = [
    {"id": 1, "name": "Rahul Sharma", "balance": 50000},
    {"id": 2, "name": "Priya Mehta",  "balance": 30000},
]

# Pydantic Models
class Account(BaseModel):
    name: str
    balance: float

class TransferRequest(BaseModel):
    from_id: int
    to_id: int
    amount: float


# Helper function
def find_account(account_id: int):
    for acc in accounts:
        if acc["id"] == account_id:
            return acc
    return None


# Routes

# GET all accounts
@app.get("/accounts")
def get_accounts():
    return accounts


# GET single account
@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    acc = find_account(account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return acc


# POST create account
@app.post("/accounts", status_code=201)
def create_account(account: Account):
    new_id = max(a["id"] for a in accounts) + 1 if accounts else 1
    new_account = {"id": new_id, "name": account.name, "balance": account.balance}
    accounts.append(new_account)
    return {"message": "Account created", "data": new_account}


# POST deposit
@app.post("/accounts/{account_id}/deposit")
def deposit(account_id: int, amount: float):
    acc = find_account(account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    acc["balance"] += amount
    return {"message": "Deposit successful", "balance": acc["balance"]}


# POST withdraw
@app.post("/accounts/{account_id}/withdraw")
def withdraw(account_id: int, amount: float):
    acc = find_account(account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if amount > acc["balance"]:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    acc["balance"] -= amount
    return {"message": "Withdrawal successful", "balance": acc["balance"]}


# POST transfer
@app.post("/transfer")
def transfer(req: TransferRequest):
    sender = find_account(req.from_id)
    receiver = find_account(req.to_id)
    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Account not found")
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if req.amount > sender["balance"]:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    sender["balance"]   -= req.amount
    receiver["balance"] += req.amount
    return {"message": "Transfer successful", "from": sender, "to": receiver}


# DELETE account
@app.delete("/accounts/{account_id}")
def delete_account(account_id: int):
    acc = find_account(account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    accounts.remove(acc)
    return {"message": "Account deleted"}