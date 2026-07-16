import {useEffect, useState} from "react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8001";

const fmt = (n) =>
  "$" +
  Number(n). toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  const fmtShort = (n) =>
    "$" + Math.round(Number(n)).toLocaleString("en-US");

  const TYPE_ICON = {
     income: "↑",
    expense: "↓",
    savings: "→",
  };

export default function App() {
  const[summary, setSummary] = useState(null);
  const[amount, setAmount] = useState("");
  const[category, setCategory] = useState("");
  const[type, setType] = useState("expense");
  const[transactions, setTransactions] = useState([]);
  const[editingId, setEditingId] = useState(null);
  const[budgetCategory, setBudgetCategory] = useState("");
  const[budgetLimit , setBudgetLimit] = useState("");
  const[budgetStatus, setBudgetStatus] = useState({});

const fetchAll = () => {
  fetch (`${API}/summary`)
  .then((r) => r.json())
  .then(setSummary)
  .catch(() => setSummary(null));

  fetch(`${API}/transactions`)
  .then((r) => r.json())
  .then(setTransactions)
  .catch(() => setTransactions([]));

  fetch(`${API}/budget-status`)
  .then((r) => r.json())
  .then(setBudgetStatus)
  .catch(() => setBudgetStatus ({}));
};
  

  useEffect(() =>{
    fetchAll();
  }, []);
  const handleSubmit = () => {
    if (!amount || !category) {
      alert("Please enter an amount and category");
      return;
    }
    const url = editingId
      ? `${API}/transactions/${editingId}`
      : `${API}/transactions`;
    const method = editingId ? "PUT" : "POST";

    fetch(url, {
      method,
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({amount: Number(amount), category,type}),
    })
    .then((r) => r.json())
    .then(() =>{
      cancelEdit();
      fetchAll();
    });
  };
  const cancelEdit = () => {
    setEditingId(null);
    setAmount("");
    setCategory("");
    setType("expense");
    
  };
  const startEdit = (tx) => {
    setEditingId(tx.id);
    setAmount(tx.amount);
    setCategory(tx.category);
    setType(tx.type);
  };
  const deleteTransaction = (id) => {
    fetch (`${API}/transactions/${id}`, {method: "DELETE" }). then(() =>
      fetchAll()
    );
  };

  const addBudget = () => {
    if(!budgetCategory || !budgetLimit) {
      alert ("Please enter a category and limit.");
      return;
    }
    fetch(`${API}/budgets`, {
      method: "POST",
      headers: {"Content-Type" : "application/json"},
      body: JSON.stringify ({
        category: budgetCategory,
        limit: Number(budgetLimit),
      }),
    })
    .then((r) => r.json())
    .then(() =>{
      setBudgetCategory("");
      setBudgetLimit("");
      fetchAll();
    });
  };
  const balance = summary?.remaining_balance ?? 0;

  return(
    <div className="app">
      <div className="topbar">
        <span className="topbar-title">Budget Tracker</span>
        <span className="topbar-date">
          {new Date().toLocaleString("en-US", { month: "long", year: "numeric" })}
        </span>
      </div>

      <div className="balance-hero">
        <div className="balance-label">Remaining balance</div>
        <div className={`balance-amount ${balance >= 0 ? "positive" : "negative"}`}>
          {summary ? fmt(balance) : "—"}
        </div>
        <div className="stats-row">
          <div className="stat">
            <div className="stat-label"><span className="stat-dot dot-income" />Income</div>
            <div className="stat-value">{summary ? fmtShort(summary.total_income) : "—"}</div>
          </div>
          <div className="stat">
            <div className="stat-label"><span className="stat-dot dot-expense" />Expenses</div>
            <div className="stat-value">{summary ? fmtShort(summary.total_expenses) : "—"}</div>
          </div>
          <div className="stat">
            <div className="stat-label"><span className="stat-dot dot-savings" />Savings</div>
            <div className="stat-value">{summary ? fmtShort(summary.total_savings) : "—"}</div>
          </div>
        </div>
      </div>

      {/* Transaction Form */}
      <div className="section-card">
        <div className="section-title">{editingId ? "Edit transaction" : "Add transaction"}</div>
        <div className="form-row three">
          <div className="field">
            <span className="field-label">Amount</span>
            <input type="number" placeholder="0.00" value={amount} onChange={(e) => setAmount(e.target.value)} />
          </div>
          <div className="field">
            <span className="field-label">Category</span>
            <input type="text" placeholder="e.g. Groceries" value={category} onChange={(e) => setCategory(e.target.value)} />
          </div>
          <div className="field">
            <span className="field-label">Type</span>
            <select value={type} onChange={(e) => setType(e.target.value)}>
              <option value="expense">Expense</option>
              <option value="income">Income</option>
              <option value="savings">Savings</option>
            </select>
          </div>
        </div>
        <div className="btn-row">
          <button className="btn-primary" onClick={handleSubmit}>
            {editingId ? "Save changes" : "Add transaction"}
          </button>
          {editingId && (
            <button className="btn-cancel" onClick={cancelEdit}>Cancel</button>
          )}
        </div>
      </div>

      <div className="section-card">
        <div className="section-title">Transactions</div>
        {transactions.length === 0 ? (
          <div className="empty-state">No transactions yet. Add one above.</div>
        ) : (
          <div className="tx-list">
            {[...transactions].reverse().map((tx) => (
              <div className="tx-item" key={tx.id}>
                <div className={`tx-icon ${tx.type}`}>{TYPE_ICON[tx.type]}</div>
                <div className="tx-info">
                  <div className="tx-category">
                    {tx.category}
                    <span className={`tx-badge badge-${tx.type}`}>{tx.type}</span>
                  </div>
                  <div className="tx-date">{tx.date}</div>
                </div>
                <div className={`tx-amount ${tx.type}`}>
                  {tx.type === "income" ? "+" : "-"}{fmt(tx.amount)}
                </div>
                <div className="tx-actions">
                  <button className="icon-btn" onClick={() => startEdit(tx)}>✎</button>
                  <button className="icon-btn del" onClick={() => deleteTransaction(tx.id)}>✕</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Budget Section */}
      <div className="section-card">
        <div className="section-title">Budgets</div>
        <div className="form-row">
          <div className="field">
            <span className="field-label">Category</span>
            <input type="text" placeholder="e.g. Food" value={budgetCategory} onChange={(e) => setBudgetCategory(e.target.value)} />
          </div>
          <div className="field">
            <span className="field-label">Monthly limit</span>
            <input type="number" placeholder="0.00" value={budgetLimit} onChange={(e) => setBudgetLimit(e.target.value)} />
          </div>
        </div>
        <div className="btn-row">
          <button className="btn-primary" onClick={addBudget}>Set budget</button>
        </div>
        {Object.keys(budgetStatus).length > 0 && (
          <div className="budget-list">
            {Object.entries(budgetStatus).map(([cat, s]) => {
              const pct = Math.min(100, Math.round((s.spent / s.budget) * 100));
              const cls = pct >= 100 ? "over" : pct >= 80 ? "warn" : "ok";
              return (
                <div className="budget-item" key={cat}>
                  <div className="budget-header">
                    <span className="budget-cat">{cat}</span>
                    <span className="budget-nums">{fmt(s.spent)} / {fmt(s.budget)}</span>
                  </div>
                  <div className="progress-track">
                    <div className={`progress-fill ${cls}`} style={{ width: `${pct}%` }} />
                  </div>
                  <div className={`budget-status-label ${cls}`}>
                    {pct >= 100 ? `Over budget by ${fmt(Math.abs(s.remaining))}` : `${fmt(s.remaining)} remaining`}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}


