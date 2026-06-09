from api_call import BASE_URL, get, post, private_key, api_key
from datetime import datetime, timezone
from dateutil import parser as dateutil_parser
import requests
import time
import uuid

def load_tickers(filepath="ticker_list.txt"):
    with open(filepath, "r") as f:
        tickers = [line.strip() for line in f if line.strip()]
    return tickers

def get_market_data():
    tickers = load_tickers()
    ## REDACTED ##

    for ticker in tickers:
        orders_placed = 0
        markets_url = f"https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker={ticker}&status=open"
        try:
            markets_response = requests.get(markets_url, timeout=10)
            markets_response.raise_for_status()
            markets_data = markets_response.json()
            time.sleep(0.25)
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            time.sleep(0.25) 
            continue

        markets = markets_data.get('markets', [])
        for market in markets:
            try:
                now = datetime.now(timezone.utc)
                ## REDACTED ##
                yes_bid = float(market.get('yes_bid_dollars', 0))
                no_bid = float(market.get('no_bid_dollars', 0))
                status = market.get('status', '')
                ticker_val = market.get('ticker', '')
            except Exception as e:
                print(f"Error parsing market data: {e}")
                continue

            if status == 'active' and (
                ## REDACTED ##
                print("\nPlacing order...")
                client_order_id = str(uuid.uuid4())
                if yes_no == 'yes':
                    order_data = {
                        "ticker": ticker_val,
                        "action": "buy",
                        "side": yes_no,
                        "count": 1,
                        "type": "limit",
                        ## REDACTED ##
                        "client_order_id": client_order_id
                    }
                else:
                    order_data = {
                        "ticker": ticker_val,
                    "action": "buy",
                    "side": yes_no,
                    "count": 1,
                    "type": "limit",
                    ## REDACTED ##
                    "client_order_id": client_order_id
                    }

                response = post('/portfolio/orders', order_data, private_key, api_key, BASE_URL)
                time.sleep(0.25)  # Sleep briefly to avoid hitting rate limits
                if response.status_code == 201:
                    order = response.json()['order']
                    orders_placed += 1
                    print(f"Order placed successfully!")
                    print(f"Order ID: {order['order_id']}")
                    print(f"Client Order ID: {client_order_id}")
                    print(f"Status: {order['status']}")
                else:
                    print(f"Error: {response.status_code} - {response.text}")
    return orders_placed

###
while True:
    try:
        response = get("/portfolio/balance")
        balance = response.json()['balance']
        print(f"Balance: ${balance / 100:.2f}")

        if balance < 1:
            print("Balance too low, breaking loop.")
            break

        orders = get_market_data()
        print(f"Cycle complete. Orders placed: {orders}")

    except Exception as e:
        print(f"Loop error: {e}")

    finally:
        time.sleep(1)  # always waits 1s before next cycle
