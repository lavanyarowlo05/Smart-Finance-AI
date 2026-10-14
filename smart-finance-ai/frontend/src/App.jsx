import { useCallback, useEffect, useRef, useState } from "react";

const STORAGE_KEY = "finora.transactions.v1";
const THEME_STORAGE_KEY = "finora.theme";
const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 2,
});

function loadTheme() {
  try {
    return localStorage.getItem(THEME_STORAGE_KEY) === "dark" ? "dark" : "light";
  } catch (error) {
    console.error("Could not read the saved appearance preference.", error);
    return "light";
  }
}

function localDateString(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function loadTransactions() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    if (!Array.isArray(saved)) return [];
    return saved.filter((value) =>
      value &&
      typeof value.id === "string" &&
      ["income", "expense"].includes(value.type) &&
      typeof value.category === "string" &&
      Number.isFinite(Number(value.amount)) &&
      typeof value.transaction_date === "string",
    );
  } catch (error) {
    console.error("Could not read browser-saved transactions.", error);
    return [];
  }
}

async function apiRequest(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  const data = await response.json();
  if (!response.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((item) => item.msg).join(", ")
      : data.detail;
    throw new Error(detail || `Request failed (${response.status}).`);
  }
  return data;
}

function Icon({ name, className = "" }) {
  const paths = {
    dashboard: <><rect x="3.5" y="3.5" width="7" height="7" rx="2" /><rect x="13.5" y="3.5" width="7" height="7" rx="2" /><rect x="3.5" y="13.5" width="7" height="7" rx="2" /><rect x="13.5" y="13.5" width="7" height="7" rx="2" /></>,
    document: <><path d="M7 4.5h8l3 3v12H7z" /><path d="M15 4.5v4h4M10 12h5M10 15.5h5" /></>,
    clock: <><circle cx="12" cy="12" r="8.5" /><path d="M12 7v5l3.5 2" /></>,
    shield: <><path d="M12 3.5 19 6v5.5c0 4.3-2.9 7.5-7 9-4.1-1.5-7-4.7-7-9V6z" /><path d="m9 12 2 2 4-4" /></>,
    calendar: <><rect x="3.5" y="5" width="17" height="15" rx="3" /><path d="M7.5 3.5v3M16.5 3.5v3M3.5 9.5h17" /></>,
    income: <><path d="M5 16 16 5M7 5h9v9" /></>,
    expense: <><path d="M5 8 16 19M7 19h9v-9" /></>,
    savings: <><path d="M12 3.5v17M17 7.5c0-1.7-2-3-5-3s-5 1.3-5 3 1.5 2.5 5 3 5 1.4 5 3-2 3-5 3-5-1.3-5-3" /></>,
    chevron: <path d="m4 6 4 4 4-4" />,
    note: <><rect x="7" y="7" width="22" height="22" rx="7" /><path d="M13 17h10M13 21h6" /></>,
  };
  return (
    <svg
      className={className}
      viewBox={name === "note" ? "0 0 36 36" : "0 0 24 24"}
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  );
}

function Brand() {
  return (
    <>
      <span className="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 32 32" fill="none">
          <path d="M7 22.5 13.3 16l4.2 4.3L25 11.5" />
          <path d="M18.8 11.5H25v6.2" />
        </svg>
      </span>
      <span className="brand-name">finora<span>.</span></span>
    </>
  );
}

function App() {
  const [theme, setTheme] = useState(loadTheme);
  const [transactions, setTransactions] = useState(loadTransactions);
  const [summary, setSummary] = useState({
    income: 0,
    expenses: 0,
    balance: 0,
    savings_rate: null,
    deficit: false,
    category_totals: {},
  });
  const [apiOnline, setApiOnline] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [transactionType, setTransactionType] = useState("expense");
  const [formError, setFormError] = useState("");
  const [toast, setToast] = useState("");
  const [runwayResult, setRunwayResult] = useState(null);
  const [runwayError, setRunwayError] = useState("");
  const [savingTransaction, setSavingTransaction] = useState(false);
  const [calculatingRunway, setCalculatingRunway] = useState(false);
  const [transactionDate, setTransactionDate] = useState(localDateString);
  const transactionDialog = useRef(null);
  const toastTimer = useRef(null);

  const notify = useCallback((message) => {
    setToast(message);
    window.clearTimeout(toastTimer.current);
    toastTimer.current = window.setTimeout(() => setToast(""), 3200);
  }, []);

  const monthTransactions = transactions.filter((transaction) => {
    const date = new Date(`${transaction.transaction_date}T00:00:00`);
    const now = new Date();
    return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
  });

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch (error) {
      console.error("Could not save the appearance preference.", error);
      notify("Could not save your appearance preference in this browser.");
    }
  }, [theme, notify]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(transactions));
    } catch (error) {
      console.error("Could not save transactions in browser storage.", error);
      notify("Could not save in this browser. Check available storage.");
    }
  }, [transactions, notify]);

  useEffect(() => {
    apiRequest("/api/health")
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false));
  }, []);

  useEffect(() => {
    let cancelled = false;
    apiRequest("/api/monthly-summary", {
      method: "POST",
      body: JSON.stringify({
        transactions: monthTransactions.map(({ type, category, amount }) => ({
          type,
          category,
          amount: Number(amount),
        })),
      }),
    })
      .then((data) => {
        if (!cancelled) {
          setSummary(data);
          setApiOnline(true);
        }
      })
      .catch((error) => {
        if (!cancelled) {
          setApiOnline(false);
          notify(`Could not update dashboard: ${error.message}`);
        }
      });
    return () => { cancelled = true; };
  }, [monthTransactions.length, transactions, notify]);

  useEffect(() => {
    if (dialogOpen && transactionDialog.current && !transactionDialog.current.open) {
      transactionDialog.current.showModal();
    } else if (!dialogOpen && transactionDialog.current?.open) {
      transactionDialog.current.close();
    }
  }, [dialogOpen]);

  useEffect(() => () => window.clearTimeout(toastTimer.current), []);

  function openTransactionDialog() {
    setFormError("");
    setTransactionType("expense");
    setTransactionDate(localDateString());
    setDialogOpen(true);
  }

  async function handleTransactionSubmit(event) {
    event.preventDefault();
    setFormError("");
    setSavingTransaction(true);
    const form = new FormData(event.currentTarget);
    const payload = {
      type: transactionType,
      category: form.get("category"),
      amount: Number(form.get("amount")),
      transaction_date: transactionDate,
    };
    try {
      const clean = await apiRequest("/api/validate/transaction", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setTransactions((current) => [
        ...current,
        { ...clean, id: crypto.randomUUID() },
      ]);
      setDialogOpen(false);
      notify("Transaction added. Your dashboard is up to date.");
    } catch (error) {
      setFormError(error.message);
    } finally {
      setSavingTransaction(false);
    }
  }

  async function handleRunwaySubmit(event) {
    event.preventDefault();
    setCalculatingRunway(true);
    setRunwayError("");
    setRunwayResult(null);
    const form = new FormData(event.currentTarget);
    try {
      const result = await apiRequest("/api/survival-months", {
        method: "POST",
        body: JSON.stringify({
          available_savings: Number(form.get("available_savings")),
          monthly_essential_expenses: Number(form.get("monthly_essential_expenses")),
          monthly_benefits: Number(form.get("monthly_benefits") || 0),
        }),
      });
      setRunwayResult(result);
      setApiOnline(true);
    } catch (error) {
      setRunwayError(error.message);
    } finally {
      setCalculatingRunway(false);
    }
  }

  function deleteTransaction(id) {
    setTransactions((current) => current.filter((transaction) => transaction.id !== id));
    notify("Transaction removed.");
  }

  function clearTransactions() {
    if (!window.confirm("Clear all transactions saved in this browser?")) return;
    setTransactions([]);
    notify("All browser-saved transactions were cleared.");
  }

  const sortedTransactions = [...transactions]
    .sort((a, b) => b.transaction_date.localeCompare(a.transaction_date));
  const categoryEntries = Object.entries(summary.category_totals || {})
    .sort((a, b) => b[1] - a[1]);
  const categoryMax = categoryEntries[0]?.[1] || 1;
  const categoryTotal = categoryEntries.reduce((sum, [, amount]) => sum + amount, 0);
  const now = new Date();

  return (
    <div className="app-shell" data-theme={theme}>
      <aside className="sidebar" aria-label="Main navigation">
        <a className="brand" href="/" aria-label="Finora home"><Brand /></a>
        <div className="nav-caption">WORKSPACE</div>
        <nav className="nav-list">
          <a className="nav-link active" href="#overview"><Icon name="dashboard" />Overview</a>
          <a className="nav-link" href="#transactions"><Icon name="document" />Transactions</a>
          <a className="nav-link" href="#runway"><Icon name="clock" />Safety runway</a>
        </nav>
        <div className="sidebar-bottom">
          <div className="privacy-card">
            <span className="privacy-icon"><Icon name="shield" /></span>
            <strong>Your money stays yours</strong>
            <span>Saved only in this browser.</span>
          </div>
          <div className="profile">
            <span className="avatar">F</span>
            <span className="profile-copy"><strong>Personal space</strong><small>Private workspace</small></span>
            <span className="profile-menu" aria-hidden="true">•••</span>
          </div>
        </div>
      </aside>

      <main className="main-content" id="overview">
        <header className="topbar">
          <a className="mobile-brand" href="/" aria-label="Finora home"><Brand /></a>
          <div className="breadcrumbs"><span>PERSONAL FINANCE</span><span className="crumb-slash">/</span><strong>OVERVIEW</strong></div>
          <div className="topbar-right">
            <span className={`api-status ${apiOnline ? "online" : "offline"}`}>
              <i />{apiOnline ? "API connected" : "API unavailable"}
            </span>
            <button
              className="icon-button theme-button"
              type="button"
              aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
              aria-pressed={theme === "dark"}
              title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
              onClick={() => setTheme((current) => current === "dark" ? "light" : "dark")}
            >
              {theme === "dark" ? "☀" : "☾"}
            </button>
            <button className="icon-button help-button" type="button" aria-label="Open API documentation" title="API documentation" onClick={() => window.open("/docs", "_blank", "noopener,noreferrer")}>?</button>
            <span className="avatar top-avatar">F</span>
          </div>
        </header>

        <div className="page-wrap">
          <section className="page-heading">
            <div>
              <div className="eyebrow"><span className="eyebrow-line" /> YOUR FINANCIAL SNAPSHOT</div>
              <h1>A clearer view of your money.</h1>
              <p className="page-subtitle">A little more clarity, a lot more confidence.</p>
            </div>
            <div className="date-pill"><Icon name="calendar" /><span>{new Intl.DateTimeFormat("en-IN", { weekday: "short", day: "numeric", month: "short", year: "numeric" }).format(now)}</span></div>
          </section>

          <section className="hero-card" aria-labelledby="balance-heading">
            <div className="hero-copy">
              <div className="hero-label"><span className="hero-label-dot" /> TOTAL NET BALANCE <span className="hero-period">· THIS MONTH</span></div>
              <h2 id="balance-heading" className="hero-amount">{currency.format(summary.balance)}</h2>
              <div className="hero-insight"><span className="insight-icon">↗</span><span>{summary.deficit ? "Expenses are higher than income this month." : summary.income > 0 ? `${currency.format(summary.balance)} left after recorded expenses.` : "Add your first transaction to see your monthly picture."}</span></div>
              <button className="button button-light" type="button" onClick={openTransactionDialog}><span className="button-plus">+</span> Add a transaction</button>
            </div>
            <div className="hero-art" aria-hidden="true">
              <div className="hero-orbit orbit-one" /><div className="hero-orbit orbit-two" /><div className="hero-orbit orbit-three" />
              <div className="hero-spark spark-one">✳</div><div className="hero-spark spark-two">✳</div>
              <div className="hero-coin"><span>₹</span><i /></div><div className="hero-art-label">MONEY<br />IN MOTION</div>
            </div>
            <div className="hero-grain" aria-hidden="true" />
          </section>

          <section className="metric-grid" aria-label="Monthly metrics">
            <MetricCard icon="income" iconClass="income-icon" label="MONEY IN" value={currency.format(summary.income)} foot="Income recorded this month" dot="green-dot" />
            <MetricCard icon="expense" iconClass="expense-icon" label="MONEY OUT" value={currency.format(summary.expenses)} foot="Expenses recorded this month" dot="orange-dot" />
            <MetricCard icon="savings" iconClass="savings-icon" label="SAVINGS RATE" value={summary.savings_rate === null ? "—" : `${summary.savings_rate.toFixed(1)}%`} foot="Of your income kept" dot="blue-dot" />
          </section>

          <section className="content-grid">
            <article className="panel spending-panel">
              <div className="panel-heading">
                <div><div className="panel-eyebrow">WHERE IT GOES</div><h2>Spending by category</h2></div>
                <span className="panel-period">THIS MONTH <Icon name="chevron" /></span>
              </div>
              <div className="category-list">
                {categoryEntries.length === 0 ? (
                  <div className="empty-inline"><span className="empty-orb">◎</span><span>Your spending breakdown will appear here.</span></div>
                ) : categoryEntries.slice(0, 5).map(([name, amount]) => (
                  <div className="category-row" key={name}>
                    <span className="category-glyph">{name.trim().slice(0, 1).toUpperCase() || "•"}</span>
                    <span className="category-name">{name}</span>
                    <span className="category-amount">{currency.format(amount)}</span>
                    <span className="category-track"><span className="category-fill" style={{ width: `${Math.max(7, amount / categoryMax * 100)}%` }} /></span>
                  </div>
                ))}
              </div>
              <div className="panel-bottom"><span>{categoryEntries.length ? `${currency.format(categoryTotal)} across ${categoryEntries.length} categor${categoryEntries.length === 1 ? "y" : "ies"}` : "No expenses recorded yet"}</span><a href="#transactions">View activity <span>↗</span></a></div>
            </article>

            <article className="panel runway-panel" id="runway">
              <div className="panel-heading"><div><div className="panel-eyebrow">A LITTLE PEACE OF MIND</div><h2>Your safety runway</h2></div><span className="runway-symbol">⌁</span></div>
              <p className="runway-intro">See how long your savings could cover essentials if income paused.</p>
              <form className="runway-form" onSubmit={handleRunwaySubmit}>
                <label>Available savings <MoneyInput name="available_savings" min="0" placeholder="60000" required /></label>
                <div className="runway-input-row">
                  <label>Essential / month <MoneyInput name="monthly_essential_expenses" min="0.01" placeholder="15000" required /></label>
                  <label>Benefits / month <MoneyInput name="monthly_benefits" min="0" placeholder="0" defaultValue="0" /></label>
                </div>
                <button className="button button-dark runway-submit" type="submit" disabled={calculatingRunway}><span>{calculatingRunway ? "Calculating…" : "Calculate runway"}</span><span>→</span></button>
              </form>
              <div className={`runway-result ${runwayError ? "error" : ""}`} aria-live="polite">
                <span className="runway-result-mark">✳</span>
                <span>{runwayError || (runwayResult ? runwayResult.unlimited ? "Your benefits cover essentials — savings aren't being depleted." : `Your savings could cover essentials for about ${runwayResult.months} month${runwayResult.months === 1 ? "" : "s"}.` : "Enter your numbers for a simple estimate.")}</span>
              </div>
            </article>
          </section>

          <section className="panel transactions-panel" id="transactions">
            <div className="panel-heading transaction-heading">
              <div><div className="panel-eyebrow">THE LITTLE DETAILS</div><h2>Recent transactions</h2></div>
              <button className="button button-outline" type="button" onClick={openTransactionDialog}><span>+</span> Add new</button>
            </div>
            <div className="table-wrap">
              <table>
                <thead><tr><th>TRANSACTION</th><th>DATE</th><th>TYPE</th><th className="amount-head">AMOUNT</th><th><span className="sr-only">Actions</span></th></tr></thead>
                <tbody>
                  {sortedTransactions.slice(0, 8).map((transaction) => (
                    <tr key={transaction.id}>
                      <td><span className="transaction-title"><span className={`transaction-icon ${transaction.type}`}>{transaction.type === "income" ? "↗" : "↙"}</span><span>{transaction.category}</span></span></td>
                      <td>{new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short", year: "numeric" }).format(new Date(`${transaction.transaction_date}T00:00:00`))}</td>
                      <td><span className={`type-badge ${transaction.type}`}>{transaction.type}</span></td>
                      <td className={`amount-cell ${transaction.type}`}>{transaction.type === "income" ? "+" : "−"}{currency.format(Number(transaction.amount))}</td>
                      <td><button className="delete-row" type="button" aria-label={`Delete ${transaction.category} transaction`} onClick={() => deleteTransaction(transaction.id)}>×</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {sortedTransactions.length === 0 && <div className="empty-state visible"><span className="empty-state-icon"><Icon name="note" /></span><strong>Your story starts with one entry</strong><span>Add a transaction to see your activity here.</span><button className="text-button" type="button" onClick={openTransactionDialog}>Add your first transaction <span>→</span></button></div>}
            </div>
            <div className="table-footer"><span>{transactions.length} transaction{transactions.length === 1 ? "" : "s"}{transactions.length > 8 ? " · showing 8 most recent" : ""}</span>{transactions.length > 0 && <button className="clear-button" type="button" onClick={clearTransactions}>Clear all</button>}</div>
          </section>

          <footer className="footer"><span>Made for a calmer relationship with money.</span><span>FINORA <i>·</i> PRIVATE BY DESIGN</span></footer>
        </div>
      </main>

      <dialog
        ref={transactionDialog}
        className="transaction-dialog"
        onCancel={() => setDialogOpen(false)}
        onClose={() => setDialogOpen(false)}
      >
        <form className="transaction-form" onSubmit={handleTransactionSubmit}>
          <div className="dialog-top"><div><div className="panel-eyebrow">A NEW MONEY MOMENT</div><h2>Add a transaction</h2></div><button className="dialog-close" type="button" aria-label="Close dialog" onClick={() => setDialogOpen(false)}>×</button></div>
          <p className="dialog-description">A few details are all it takes to keep your picture up to date.</p>
          <label className="form-label">Transaction type
            <span className="type-switch">
              <button className={`type-choice ${transactionType === "expense" ? "selected" : ""}`} type="button" onClick={() => setTransactionType("expense")}>Expense</button>
              <button className={`type-choice ${transactionType === "income" ? "selected" : ""}`} type="button" onClick={() => setTransactionType("income")}>Income</button>
            </span>
          </label>
          <label className="form-label">Category<input name="category" type="text" maxLength="60" placeholder="e.g. Groceries, Salary" required /></label>
          <div className="dialog-fields">
            <label className="form-label">Amount <span className="dialog-amount-input"><span>₹</span><input name="amount" type="number" min="0.01" step="0.01" placeholder="0.00" required /></span></label>
            <label className="form-label">Date<input name="transaction_date" type="date" value={transactionDate} onChange={(event) => setTransactionDate(event.target.value)} required /></label>
          </div>
          <div className="form-error" role="alert">{formError}</div>
          <div className="dialog-actions"><button className="button button-outline" type="button" onClick={() => setDialogOpen(false)}>Cancel</button><button className="button button-dark" type="submit" disabled={savingTransaction}><span>{savingTransaction ? "Saving…" : "Save transaction"}</span><span>→</span></button></div>
          <p className="local-note"><Icon name="shield" /> Stored in this browser only</p>
        </form>
      </dialog>
      <div className={`toast ${toast ? "show" : ""}`} role="status" aria-live="polite">{toast}</div>
    </div>
  );
}

function MetricCard({ icon, iconClass, label, value, foot, dot }) {
  return (
    <article className="metric-card">
      <div className="metric-top"><span className={`metric-icon ${iconClass}`}><Icon name={icon} /></span><span className="metric-kicker">{label}</span><span className="metric-menu">•••</span></div>
      <div className="metric-value">{value}</div>
      <div className="metric-foot"><span className={`metric-dot ${dot}`} /><span>{foot}</span></div>
    </article>
  );
}

function MoneyInput({ name, min, placeholder, required = false, defaultValue }) {
  return (
    <span className="input-wrap"><span>₹</span><input name={name} type="number" min={min} step="0.01" placeholder={placeholder} defaultValue={defaultValue} required={required} /></span>
  );
}

export default App;
