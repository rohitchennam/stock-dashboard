# Stock Intelligence Dashboard

A mini financial data platform built with FastAPI, Pandas, and Chart.js.
Tracks real NSE stock data for 10 Indian companies with ML price forecasting.

## Features

- Real-time NSE stock data via yfinance
- Calculated metrics: Daily Return, 7D Moving Average, 52W High/Low, Volatility
- REST API with FastAPI
- Interactive dashboard with Chart.js
- 7-day ML price prediction using Linear Regression
- Dockerized for easy deployment

## Tech Stack

| Layer    | Technology                       |
| -------- | -------------------------------- |
| Data     | yfinance, Pandas, NumPy          |
| Backend  | FastAPI, Uvicorn                 |
| ML       | Scikit-learn (Linear Regression) |
| Frontend | HTML, Chart.js                   |
| DevOps   | Docker                           |

## API Endpoints

| Method | Endpoint                       | Description                         |
| ------ | ------------------------------ | ----------------------------------- |
| GET    | `/companies`                   | List all tracked companies          |
| GET    | `/data/{symbol}?days=30`       | Last N days of stock data           |
| GET    | `/summary/{symbol}`            | 52W high/low, avg, volatility       |
| GET    | `/compare?symbol1=X&symbol2=Y` | Normalized comparison + correlation |
| GET    | `/movers`                      | Top 3 gainers and losers            |
| GET    | `/predict/{symbol}`            | 7-day ML price forecast             |

## Setup & Run

### Local

```bash
git init
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker

```bash
docker build -t stock-dashboard .
docker run -p 8000:8000 stock-dashboard
```

## Project Structure

```bash
stock-dashboard/
├── app/
│   ├── main.py       # FastAPI routes
│   ├── data.py       # Data fetching & processing
│   └── ml.py         # ML prediction
├── static/
│   └── index.html    # Frontend dashboard
├── data/             # Cached CSV files
├── Dockerfile
├── requirements.txt
└── README.md
```

## Tracked Companies

```bash
INFY, TCS, RELIANCE, HDFCBANK, WIPRO, ICICIBANK, HINDUNILVR, SBIN, BAJFINANCE, MARUTI
```
