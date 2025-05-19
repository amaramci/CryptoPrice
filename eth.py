import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objs as go

def fetch_eth_prices_last_365_days():
    url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': '365',
        'interval': 'daily'
    }

    print("Fetching data from CoinGecko...")
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception("Failed to fetch data from CoinGecko.")

    data = response.json()
    prices = data.get('prices', [])

    if not prices:
        raise Exception("No price data returned.")

    date_price = [(datetime.utcfromtimestamp(p[0] / 1000).date(), p[1]) for p in prices]
    df = pd.DataFrame(date_price, columns=['date', 'price'])
    return df

def calculate_average_and_median_price(df):
    average_price = df['price'].mean()
    median_price = df['price'].median()
    return average_price, median_price

def filter_outliers(df, avg, median):
    upper_avg_limit = avg * 1.55
    lower_avg_limit = avg * 0.55
    upper_median_limit = median * 1.55
    lower_median_limit = median * 0.55

    filtered_df = df[
        (df['price'] <= upper_avg_limit) &
        (df['price'] >= lower_avg_limit) &
        (df['price'] <= upper_median_limit) &
        (df['price'] >= lower_median_limit)
    ]
    return filtered_df

def plot_interactive_chart(df, filtered_df, avg, median, new_avg, new_median):
    df['change'] = df['price'].diff()
    df['percent_change'] = df['price'].pct_change() * 100

    jumps = df[df['percent_change'] >= 10]
    drops = df[df['percent_change'] <= -10]

    fig = go.Figure()

    # ✅ Tanka crna linija za originalne ETH cene
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['price'],
        mode='lines',
        name='ETH Price',
        line=dict(color='black', width=1),
        hovertemplate='Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
    ))

    # 🔵 Skokovi – jaka plava boja
    fig.add_trace(go.Scatter(
        x=jumps['date'],
        y=jumps['price'],
        mode='markers',
        name='Jumps > 10%',
        marker=dict(color='#007bff', size=8, symbol='triangle-up'),
        hovertemplate='Date: %{x}<br>Price: $%{y:.2f}<br>Change: %{customdata:.2f} %<extra></extra>',
        customdata=jumps['percent_change']
    ))

    # 🔴 Padovi – jaka crvena boja
    fig.add_trace(go.Scatter(
        x=drops['date'],
        y=drops['price'],
        mode='markers',
        name='Drops > 10%',
        marker=dict(color='#ff0033', size=8, symbol='triangle-down'),
        hovertemplate='Date: %{x}<br>Price: $%{y:.2f}<br>Change: %{customdata:.2f} %<extra></extra>',
        customdata=drops['percent_change']
    ))

    # ➖ Horizontalne linije za avg i median
    for y_val, color, label in [
        (avg, 'red', f"Avg: ${avg:.2f}"),
        (median, 'orange', f"Median: ${median:.2f}"),
        (new_avg, 'green', f"Filtered Avg: ${new_avg:.2f}"),
        (new_median, 'blue', f"Filtered Median: ${new_median:.2f}")
    ]:
        fig.add_trace(go.Scatter(
            x=[df['date'].min(), df['date'].max()],
            y=[y_val, y_val],
            mode='lines',
            line=dict(color=color, dash='dash'),
            name=label,
            hoverinfo='skip'
        ))

    fig.update_layout(
        title='Ethereum Price - Last 365 Days (Interactive)',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        hovermode='x unified',
        height=600
    )

    fig.show()

def main():
    df = fetch_eth_prices_last_365_days()
    avg, median = calculate_average_and_median_price(df)
    print(f"Original average Ethereum price: ${avg:.2f}")
    print(f"Original median Ethereum price:  ${median:.2f}")

    filtered_df = filter_outliers(df, avg, median)
    new_avg, new_median = calculate_average_and_median_price(filtered_df)

    print("\nAfter removing outliers:")
    print(f"Filtered average Ethereum price: ${new_avg:.2f}")
    print(f"Filtered median Ethereum price:  ${new_median:.2f}")

    plot_interactive_chart(df, filtered_df, avg, median, new_avg, new_median)

if __name__ == "__main__":
    main()
