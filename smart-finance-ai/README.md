# Smart Finance AI

Smart Finance AI is a personal-finance dashboard built with React and a Python/FastAPI backend. It summarizes monthly income and expenses, validates transactions, and estimates how long savings can cover essential expenses. Transactions are saved in the browser's local storage; the backend does not store them.

## Run the application

### Production-style dashboard served by FastAPI

From the project root in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Set-Location .\frontend
npm install
npm run build
Set-Location ..\backend
python -m uvicorn api:app --reload
```

Open the dashboard at [http://127.0.0.1:8000](http://127.0.0.1:8000), API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs), or health status at [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health). Stop the server with `Ctrl+C`.

The Vite build creates `frontend/dist/`, which FastAPI serves at `/`. Build the frontend again after changing React or CSS. If the bundle is absent, the API remains available and `/` returns an explanatory HTTP 503 response.

### Frontend development

Use two PowerShell terminals from the project root. In the first, start the API:

```powershell
.\.venv\Scripts\Activate.ps1
Set-Location .\backend
python -m uvicorn api:app --reload
```

In the second, start Vite:

```powershell
Set-Location .\frontend
npm install
npm run dev
```

Open the local URL printed by Vite (normally [http://localhost:5173](http://localhost:5173)). Vite proxies API requests to the FastAPI server on port 8000.

## Tests

From the project root, with the virtual environment active:

```powershell
python -m pytest -q
```

## Project structure

```text
smart-finance-ai/
├── backend/
│   ├── api.py
│   ├── routes/
│   │   └── finance.py
│   ├── schemas/
│   │   └── finance.py
│   └── services/
│       ├── financial_engine.py
│       ├── survival_engine.py
│       └── validators.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── styles.css
│   └── vite.config.js
├── tests/
├── requirements.txt
├── pyproject.toml
├── pytest.ini
└── README.md
```

## Backend overview

- `backend/api.py` creates the FastAPI app, registers the finance routes and health check, and serves the built React dashboard. Run it from `backend/` with `python -m uvicorn api:app --reload`.
- `backend/routes/finance.py` defines the HTTP endpoints and translates service errors into HTTP responses.
- `backend/schemas/finance.py` defines and validates request data.
- `backend/services/financial_engine.py` contains balance, savings-rate, deficit, totals, category totals, and monthly-summary calculations.
- `backend/services/survival_engine.py` calculates the savings runway.
- `backend/services/validators.py` validates and normalizes transaction input.
- `frontend/src/App.jsx` renders the dashboard, submits transactions to the API, and manages browser-local transaction storage.
- `frontend/styles.css` contains the responsive dashboard styles; Vite compiles the React app into `frontend/dist/`.
- `tests/` covers finance calculations, survival estimates, and transaction validation.

## API endpoints

All listed POST requests accept JSON. Invalid request data returns HTTP `422`.

| Method and path | Purpose |
|---|---|
| `POST /api/balance` | Calculate income minus expenses. |
| `GET /api/balance?income=25000&expenses=18000` | Calculate income minus expenses using query parameters. |
| `POST /api/savings-rate` | Calculate savings as a percentage of income. |
| `POST /api/deficit` | Check whether the balance is negative. |
| `POST /api/total` | Sum a list of amounts. |
| `POST /api/category-totals` | Sum expenses grouped by category. |
| `POST /api/monthly-summary` | Return income, expenses, balance, savings rate, deficit, and category totals. |
| `POST /api/survival-months` | Estimate how long available savings cover essential expenses after benefits. |
| `POST /api/validate/transaction` | Validate and normalize a transaction. |
| `GET /api/health` | Check API availability. |

If benefits fully cover essential expenses, the survival endpoint returns `{"months": null, "unlimited": true}`.
