# Crypto Market Regime Forecaster

This project is a Streamlit application designed to forecast market regimes for cryptocurrencies like Bitcoin (BTC) and Ethereum (ETH). It uses historical price data to determine current market regimes and allows users to forecast future regimes based on hypothetical price changes.

## Features

- **Market Regime Analysis**: Classifies market conditions into different regimes based on price trends and volatility.
- **Data Fetching and Processing**: Downloads historical price data for BTC and ETH from Yahoo Finance.
- **Regime Forecasting**: Allows users to input hypothetical price changes to forecast future market regimes.
- **Interactive Visualizations**: Displays current market status and historical price charts with regime heatmaps.

## Regime Definitions

The application classifies market conditions into the following regimes:

1. **Above Avg Vol Bull Trend**: Price is above both short and long moving averages with high volatility.
2. **Below Avg Vol Bull Trend**: Price is above both short and long moving averages with low volatility.
3. **Above Avg Vol Sideways**: Price is between moving averages with high volatility.
4. **Below Avg Vol Sideways**: Price is between moving averages with low volatility.
5. **Above Avg Vol Bear Trend**: Price is below both short and long moving averages with high volatility.
6. **Below Avg Vol Bear Trend**: Price is below both short and long moving averages with low volatility.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/crypto-market-regime-forecaster.git
   cd crypto-market-regime-forecaster
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run regime_app.py
   ```

## Usage

- **Refresh Data**: Click the "Refresh Data" button to download the latest market data.
- **Forecast Tomorrow's Regime**: Input expected returns for BTC and ETH to forecast the next day's market regime.
- **View Historical Data**: Explore historical price charts with regime heatmaps to understand past market conditions.

## Dependencies

- `streamlit`: For building the interactive web application.
- `vectorbt`: For financial data analysis and backtesting.
- `pandas`: For data manipulation and analysis.
- `numpy`: For numerical computations.
- `numba`: For optimizing performance with JIT compilation.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
