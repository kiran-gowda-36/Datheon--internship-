"""Stock Portfolio Performance Tracker.

Enter stock tickers, buy prices and share quantities. The program looks up
current prices, shows total portfolio value and the gain/loss % for each
holding, and logs the summary to portfolio_summary.csv.

Run with:  python portfolio.py
"""

import csv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(BASE_DIR, "constituents.txt")   # S&P 500 dataset
SUMMARY_FILE = os.path.join(BASE_DIR, "portfolio_summary.csv")

CSV_HEADER = [
    "Run Time", "Ticker", "Company", "Sector", "Shares", "Buy Price",
    "Invested", "Current Price", "Current Value", "Gain/Loss", "Gain/Loss %",
]


# ---------- loading the S&P 500 dataset ----------

def load_companies():
    """Return {ticker: (company name, sector)} from the dataset CSV."""
    companies = {}
    try:
        with open(DATASET_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                companies[row["Symbol"].upper()] = (row["Security"], row["GICS Sector"])
    except OSError:
        print("(Dataset constituents.txt not found - ticker names unavailable.)")
    return companies


# ---------- price lookup ----------

def fetch_live_price(ticker):
    """Try to get the latest price with yfinance. Return None if unavailable."""
    try:
        import yfinance as yf
        price = yf.Ticker(ticker.replace(".", "-")).fast_info["last_price"]
        return float(price) if price else None
    except Exception:
        return None


def ask_float(prompt, allow_zero=False):
    """Keep asking until the user types a valid positive number."""
    while True:
        try:
            value = float(input(prompt).strip().replace(",", ""))
        except ValueError:
            print("Please enter a number.")
            continue
        if value > 0 or (allow_zero and value == 0):
            return value
        print("The number must be greater than zero.")


def get_current_price(ticker):
    """Live price if possible, otherwise ask the user to type it in."""
    price = fetch_live_price(ticker)
    if price is not None:
        return price
    print(f"Could not fetch a live price for {ticker}.")
    return ask_float(f"  Enter the current price of {ticker}: ")


# ---------- building the portfolio ----------

def add_position(portfolio, ticker, price, shares):
    """Add shares to the portfolio dictionary (merges repeat buys)."""
    if ticker in portfolio:
        old = portfolio[ticker]
        total_shares = old["shares"] + shares
        total_cost = old["shares"] * old["buy_price"] + shares * price
        portfolio[ticker] = {"shares": total_shares, "buy_price": total_cost / total_shares}
    else:
        portfolio[ticker] = {"shares": shares, "buy_price": price}


def collect_positions(companies):
    portfolio = {}   # {"AAPL": {"shares": 10, "buy_price": 150.0}, ...}
    print("Enter your holdings. Type 'done' when finished.\n")
    while True:
        ticker = input("Ticker symbol (e.g. AAPL): ").strip().upper()
        if ticker == "DONE":
            if portfolio:
                break
            print("Add at least one holding first.")
            continue
        if companies and ticker not in companies:
            print(f"'{ticker}' is not in the S&P 500 dataset. Check the symbol.")
            continue
        if not ticker:
            continue
        name = companies.get(ticker, ("", ""))[0]
        if name:
            print(f"  -> {name}")
        price = ask_float("  Buy price per share: ")
        shares = ask_float("  Number of shares: ")
        add_position(portfolio, ticker, price, shares)
        print("  Added.\n")
    return portfolio


# ---------- calculations ----------

def analyse(portfolio, companies):
    """Return a list of result rows (dicts), one per holding."""
    results = []
    for ticker, pos in portfolio.items():
        current = get_current_price(ticker)
        invested = pos["shares"] * pos["buy_price"]
        value = pos["shares"] * current
        gain = value - invested
        results.append({
            "ticker": ticker,
            "company": companies.get(ticker, ("", ""))[0],
            "sector": companies.get(ticker, ("", ""))[1],
            "shares": pos["shares"],
            "buy_price": pos["buy_price"],
            "invested": invested,
            "current_price": current,
            "value": value,
            "gain": gain,
            "gain_pct": gain / invested * 100,
        })
    return results


def totals(results):
    invested = sum(r["invested"] for r in results)
    value = sum(r["value"] for r in results)
    gain = value - invested
    return invested, value, gain, gain / invested * 100


# ---------- output ----------

def print_report(results):
    line = "-" * 78
    print("\n" + "=" * 78)
    print("PORTFOLIO PERFORMANCE REPORT".center(78))
    print("=" * 78)
    print(f"{'Ticker':<8}{'Shares':>9}{'Buy':>11}{'Now':>11}{'Invested':>13}{'Value':>13}{'Gain %':>10}")
    print(line)
    for r in results:
        print(f"{r['ticker']:<8}{r['shares']:>9.2f}{r['buy_price']:>11.2f}"
              f"{r['current_price']:>11.2f}{r['invested']:>13.2f}{r['value']:>13.2f}"
              f"{r['gain_pct']:>+9.2f}%")
    print(line)
    invested, value, gain, pct = totals(results)
    print(f"Total invested capital : {invested:>12,.2f}")
    print(f"Current market value   : {value:>12,.2f}")
    print(f"Total gain/loss        : {gain:>+12,.2f}  ({pct:+.2f}%)")
    print("=" * 78)


def save_summary(results):
    """Append this run to portfolio_summary.csv (header written once)."""
    run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_file = not os.path.exists(SUMMARY_FILE) or os.path.getsize(SUMMARY_FILE) == 0
    with open(SUMMARY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(CSV_HEADER)
        for r in results:
            writer.writerow([
                run_time, r["ticker"], r["company"], r["sector"],
                f"{r['shares']:.2f}", f"{r['buy_price']:.2f}", f"{r['invested']:.2f}",
                f"{r['current_price']:.2f}", f"{r['value']:.2f}",
                f"{r['gain']:.2f}", f"{r['gain_pct']:.2f}",
            ])
        invested, value, gain, pct = totals(results)
        writer.writerow([run_time, "TOTAL", "", "", "", "", f"{invested:.2f}", "",
                         f"{value:.2f}", f"{gain:.2f}", f"{pct:.2f}"])
    print(f"\nSummary saved to {os.path.basename(SUMMARY_FILE)}")


def main():
    print("=== STOCK PORTFOLIO TRACKER ===\n")
    companies = load_companies()
    portfolio = collect_positions(companies)
    results = analyse(portfolio, companies)
    print_report(results)
    save_summary(results)


if __name__ == "__main__":
    main()
