# app/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.ml import predict_next_7_days
from app.data import (
    COMPANIES, get_last_n_days, get_summary,
    compare_stocks, preload_all
)
import uvicorn

app = FastAPI(
    title="Stock Data Intelligence Dashboard",
    description="Mini financial data platform with real NSE stock data",
    version="1.0.0"
)

# Serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    preload_all()


@app.get("/", include_in_schema=False)
def root():
    return FileResponse("static/index.html")


# ── Endpoint 1: List all companies ──────────────────────────────────────────
@app.get("/companies")
def list_companies():
    return [
        {"symbol": symbol, "name": name}
        for symbol, name in COMPANIES.items()
    ]


# ── Endpoint 2: Last N days of stock data ───────────────────────────────────
@app.get("/data/{symbol}")
def get_stock_data(symbol: str, days: int = Query(default=30, ge=7, le=365)):
    symbol = symbol.upper()
    if symbol not in COMPANIES:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")
    try:
        df = get_last_n_days(symbol, days)
        return {
            "symbol": symbol,
            "name": COMPANIES[symbol],
            "days": days,
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Endpoint 3: Summary (52w high/low, avg, volatility) ─────────────────────
@app.get("/summary/{symbol}")
def stock_summary(symbol: str):
    symbol = symbol.upper()
    if symbol not in COMPANIES:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")
    try:
        return get_summary(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Endpoint 4: Compare two stocks ──────────────────────────────────────────
@app.get("/compare")
def compare(
    symbol1: str = Query(..., description="First stock symbol e.g. INFY"),
    symbol2: str = Query(..., description="Second stock symbol e.g. TCS")
):
    s1, s2 = symbol1.upper(), symbol2.upper()
    for s in [s1, s2]:
        if s not in COMPANIES:
            raise HTTPException(status_code=404, detail=f"Symbol '{s}' not found")
    try:
        return compare_stocks(s1, s2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Endpoint 5: Top gainers & losers (today) ────────────────────────────────
@app.get("/movers")
def top_movers():
    results = []
    for symbol in COMPANIES:
        try:
            s = get_summary(symbol)
            results.append({"symbol": symbol, "name": s["name"], "return": s["latest_return"]})
        except:
            pass
    results.sort(key=lambda x: x["return"], reverse=True)
    return {
        "gainers": results[:3],
        "losers": results[-3:][::-1]
    }

# ── Endpoint 6: ML Price Prediction ─────────────────────────────────────────
@app.get("/predict/{symbol}")
def predict(symbol: str):
    symbol = symbol.upper()
    if symbol not in COMPANIES:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")
    try:
        from app.data import load_data
        df = load_data(symbol)
        result = predict_next_7_days(df)
        return {
            "symbol": symbol,
            "name": COMPANIES[symbol],
            "model": "Linear Regression (last 60 days)",
            "predictions": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)