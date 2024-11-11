import streamlit as st
import vectorbt as vbt
import pandas as pd
import numpy as np
from numba import njit

# Disable progress bar
# vbt.settings.pbar['disable'] = True


@njit
def rolling_mean_nb(arr, window):
    out = np.empty_like(arr)
    for i in range(len(arr)):
        if i < window - 1:
            out[i] = np.nan
        else:
            out[i] = np.mean(arr[i - window + 1 : i + 1])
    return out


@njit
def annualized_volatility_nb(returns, window):
    out = np.empty_like(returns)
    for i in range(len(returns)):
        if i < window - 1:
            out[i] = np.nan
        else:
            out[i] = np.std(returns[i - window + 1 : i + 1]) * np.sqrt(365)
    return out


@njit
def determine_regime_nb(price, ma_short, ma_long, vol_short, avg_vol_threshold):
    regimes = np.empty_like(price, dtype=np.int32)
    for i in range(len(price)):
        if np.isnan(ma_short[i]) or np.isnan(ma_long[i]) or np.isnan(vol_short[i]):
            regimes[i] = -1  # Unknown
        elif price[i] > ma_short[i] and price[i] > ma_long[i]:
            if vol_short[i] > avg_vol_threshold:
                regimes[i] = 1  # Above Avg Vol Bull Trend
            else:
                regimes[i] = 2  # Below Avg Vol Bull Trend
        elif price[i] < ma_short[i] and price[i] < ma_long[i]:
            if vol_short[i] > avg_vol_threshold:
                regimes[i] = 5  # Above Avg Vol Bear Trend
            else:
                regimes[i] = 6  # Below Avg Vol Bear Trend
        else:
            if vol_short[i] > avg_vol_threshold:
                regimes[i] = 3  # Above Avg Vol Sideways
            else:
                regimes[i] = 4  # Below Avg Vol Sideways
    return regimes


@njit
def calculate_regimes_nb(
    price, returns, ma_short_window, ma_long_window, vol_short_window, avg_vol_window
):
    ma_short = rolling_mean_nb(price, ma_short_window)
    ma_long = rolling_mean_nb(price, ma_long_window)
    vol_short = annualized_volatility_nb(returns, vol_short_window)
    avg_vol_threshold = np.nanmean(annualized_volatility_nb(returns, avg_vol_window))
    regimes = determine_regime_nb(
        price, ma_short, ma_long, vol_short, avg_vol_threshold
    )
    return regimes


RegimeIndicator = vbt.IndicatorFactory(
    class_name="RegimeIndicator",
    short_name="regime",
    input_names=["price", "returns"],
    param_names=[
        "ma_short_window",
        "ma_long_window",
        "vol_short_window",
        "avg_vol_window",
    ],
    output_names=["regimes"],
).from_apply_func(calculate_regimes_nb)


@st.cache_data
def fetch_and_process_data():
    tickers = ["BTC-USD", "ETH-USD"]
    start_date = "2016-01-01"
    end_date = "now"

    yf_data = vbt.YFData.download(tickers, start=start_date, end=end_date)
    close_prices = yf_data.get("Close")

    daily_data = {}
    for ticker in tickers:
        daily = close_prices[ticker].to_frame()
        daily["Return"] = daily[ticker].pct_change()

        regime_indicator = RegimeIndicator.run(
            daily[ticker],
            daily["Return"],
            ma_short_window=21,
            ma_long_window=88,
            vol_short_window=21,
            avg_vol_window=365,
        )
        daily["Regime"] = regime_indicator.regimes

        daily_data[ticker] = daily

    return daily_data


# Define regime descriptions
regime_descriptions = {
    1: "Above Avg Vol Bull Trend",
    2: "Below Avg Vol Bull Trend",
    3: "Above Avg Vol Sideways",
    4: "Below Avg Vol Sideways",
    5: "Above Avg Vol Bear Trend",
    6: "Below Avg Vol Bear Trend",
}


def forecast_next_regime(daily_data, ticker, hypothetical_change=0.01):
    """
    Forecast the next market regime based on a hypothetical price change.

    Parameters:
    daily_data (pd.DataFrame): DataFrame containing daily price and return data.
    ticker (str): The ticker symbol for the asset (e.g., 'BTC-USD').
    hypothetical_change (float): The hypothetical percentage change in price for tomorrow.

    Returns:
    int: The projected market regime for tomorrow.
    """
    # Add a hypothetical price for tomorrow
    hypothetical_price = daily_data[ticker].iloc[-1] * (1 + hypothetical_change)

    # Create a new row with the hypothetical price
    new_row = pd.DataFrame(
        {ticker: [hypothetical_price], "Return": [np.nan]},
        index=[daily_data.index[-1] + pd.Timedelta(days=1)],
    )

    # Concatenate the new row to the existing DataFrame
    extended_data = pd.concat([daily_data, new_row])

    # Recalculate returns for the extended DataFrame
    extended_data["Return"] = extended_data[ticker].pct_change()

    # Recalculate regimes with the extended data
    regime_indicator_extended = RegimeIndicator.run(
        extended_data[ticker],
        extended_data["Return"],
        ma_short_window=21,
        ma_long_window=88,
        vol_short_window=21,
        avg_vol_window=365,
    )

    # Get the projected regime for tomorrow
    projected_regime = regime_indicator_extended.regimes.iloc[-1]

    return projected_regime


# Streamlit app
st.title("Crypto Market Regime Forecaster")

# Display regime definitions
st.subheader("Regime Definitions")
col1, col2 = st.columns(2)

for i, (regime_number, description) in enumerate(regime_descriptions.items()):
    with col1 if i % 2 == 0 else col2:
        st.markdown(f"**Regime {regime_number}:** {description}")

if st.button("Refresh Data"):
    st.cache_data.clear()
    st.success("Data refreshed successfully!")

daily_data = fetch_and_process_data()

# Display current prices and regimes
st.subheader("Current Market Status")
col1, col2 = st.columns(2)
for i, (ticker, data) in enumerate(daily_data.items()):
    with col1 if i == 0 else col2:
        st.metric(f"{ticker} Price", f"${data[ticker].iloc[-1]:.2f}")
        st.metric(f"{ticker} Current Regime", data["Regime"].iloc[-1])

# User input for hypothetical returns
st.subheader("Forecast Tomorrow's Regime")
col1, col2 = st.columns(2)
changes = {}
for i, ticker in enumerate(daily_data.keys()):
    with col1 if i == 0 else col2:
        changes[ticker] = st.number_input(
            f"{ticker} Expected Return (%)", value=0.0, step=0.1
        )

if st.button("Forecast Regimes"):
    st.subheader("Projected Regimes for Tomorrow")
    col1, col2 = st.columns(2)
    for i, (ticker, data) in enumerate(daily_data.items()):
        projected_regime = forecast_next_regime(
            data, ticker, hypothetical_change=changes[ticker] / 100
        )
        with col1 if i == 0 else col2:
            st.metric(f"{ticker} Projected Regime", projected_regime)

# Display historical price charts with regime heatmap
st.subheader("Historical Price Charts with Regime Heatmap")
for ticker, data in daily_data.items():
    fig = data[ticker].vbt.overlay_with_heatmap(data["Regime"])
    st.plotly_chart(fig)
