import {useEffect, useState} from "react";

function App(){
  const[summary, setSummary] = useState(null);
  const[amount, setAmount] = useState("");
  const[category, setCategory] = useState("");
  const[type, setType] = useState("expense");
  const[transactions, setTransactions] = useState([]);
  const[editingId, setEditingId] = useState(null);
  const[isEditing, setIsEditing] = useState(false);
  const[budgetCategory, setBudgetCategory] = useState("");
  const[budgetLimit , setBudgetLimit] = useState("");
  const[budgetStatus, setBudgetStatus] = useState({});

  const fetchBudgetStatus = () => {
    fetch("http://127.0.0.1:8001/budget-status")
    .then((response) => response.json())
    .then((data) => {
      setBudgetStatus(data)
    });
  };
  const fetchSummary = () =>{
    fetch("http://127.0.0.1:8001/summary")
    .then((response) => response.json())
    .then((data) => {
      setSummary(data);
    })
    .catch((error) =>{
      console.error("Error fetching summary",error)
    });
  };
const fetchTransactions = () => {
  fetch("http://127.0.0.1:8001/transactions")
  .then((response) => response.json())
  .then((data) => {
    setTransactions(data);
  });
};

  useEffect(() =>{
    fetchSummary();
    fetchTransactions();
    fetchBudgetStatus();
  }, []);
  const addTransaction = () => {
    fetch("http://127.0.0.1:8001/transactions",{
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        amount:Number(amount),
        category:category,
        type: type
      })
    })
    .then((response) => response.json())
    .then((data) =>{
      console.log("Transaction added",data)
      fetchSummary();
      fetchTransactions();
      setAmount("")
      setCategory("")
      setType("expense")
    });
    console.log ({
      amount,
      category,
      type
    });
  };
  const deleteTransaction = (transactionId) => {
    fetch(`http://127.0.0.1:8001/transactions/${transactionId}`, {
      method: "DELETE"
    })
    .then((response) => response.json())
    .then((data) => {
      console.log("Deleted:",data);
      fetchSummary();
      fetchTransactions();
    });
  };
  const startEdit = (transaction) =>{
    setEditingId(transaction.id);
    setAmount(transaction.amount);
    setCategory(transaction.category);
    setType(transaction.type);
    setIsEditing(true);
  };

  const updateTransaction = () => {
    fetch(`http://127.0.0.1:8001/transactions/${editingId}`,{
      method: "PUT",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        amount: Number(amount),
        category: category,
        type: type
      })
    })
    .then ((response) => response.json())
    .then((data) => {
      console.log("Updated:",data);
      fetchSummary();
      fetchTransactions();
      setAmount("");
      setCategory("");
      setType("expense");
      setEditingId(null);
      setIsEditing(false)
    });
  };
  const addBudget = () => {
    fetch("http://127.0.0.1:8001/budgets",{
      method: "POST",
      headers: {
        "Content-Type" :"application/json"
      },
      body: JSON.stringify({
        category: budgetCategory,
        limit: Number(budgetLimit)
      })
    })
    .then((response) => response.json())
    .then((data) => {
      console.log("Budget added:", data)
      fetchBudgetStatus();
      fetchSummary();
      setBudgetCategory("");
      setBudgetLimit("")
    });
  };
  return (
  <div>
    <h1>Budget Tracker</h1>

    {summary === null ? (
      <p>Loading summary...</p>
    ) : (
      <div>
        <p>Total Income: ${summary.total_income}</p>
        <p>Total Expenses: ${summary.total_expenses}</p>
        <p>Total Savings: ${summary.total_savings}</p>
        <p>Remaining Balance: ${summary.remaining_balance}</p>
        <p> Last Updated : {summary.last_updated}</p>
      </div>
    )}
    <h2>Add Transaction</h2>
    <input
      type="number"
      placeholder="Amount"
      value={amount}
      onChange={(e) => setAmount(e.target.value)}
    />
    <input
      type="text"
      placeholder="Category"
      value={category}
      onChange={(e) => setCategory(e.target.value)}
    />
    <select value={type} onChange={(e) => setType(e.target.value)}>
      <option value="expense">Expense</option>
      <option value="income">Income</option>
      <option value="savings">Savings</option>
    </select>
    <button onClick={isEditing ? updateTransaction: addTransaction}>
      {isEditing ? "Update Transaction" : "Add Transaction"}
    </button>

    <h2>Transactions</h2>
    {transactions.map((transaction) => (
      <div key={transaction.id}>
        <p>
          {transaction.date} - {transaction.type} - {transaction.category} - ${transaction.amount}
        </p>
        <button onClick={() => deleteTransaction(transaction.id)}>
          Delete
        </button>
        <button onClick={() => startEdit(transaction)}>
          Edit
          </button>
      </div>

    ))}


  <h2> Set Budget </h2>
  <input
    type="text"
    placeholder="Category"
    value={budgetCategory}
    onChange = {(e) => setBudgetCategory(e.target.value)}
  />
  <input
      type="number"
      placeholder="Budget Limit"
      value={budgetLimit}
      onChange={(e) => setBudgetLimit(e.target.value)}
      />

  <button onClick = {addBudget}>
    Set Budget
  </button>
  <h2> Budget Status</h2>

  {Object.entries(budgetStatus).map(([category,status]) => (
    <div key={category}>
      <p>
        {category}: Spent ${status.spent}/ Budget ${status.budget}
      </p>
      <p> Remaining: ${status.remaining}</p>
      <p>
        Status: {status.over_budget ? "Over Budget" : "Under Budget"}
      </p>
    </div>
  ))}
  </div>
  );
  }
export default App;
