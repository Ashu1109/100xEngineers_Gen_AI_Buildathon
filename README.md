
https://github.com/user-attachments/assets/34790ea3-9d21-433d-a531-2c2f7e9c30fc
# Crypto Analysis and Trading Platform

A powerful application that provides detailed cryptocurrency analysis and automated trading capabilities using the Binance API.

<img width="1440" alt="Screenshot 2025-06-02 at 10 15 02 AM" src="https://github.com/user-attachments/assets/05d00c69-7855-45f3-9739-719868aa7388" />




## Video Demonstrations

### Crypto Analysis Feature
https://github.com/user-attachments/assets/5daea363-5f54-405d-9697-0625ac0464f8


*This video demonstrates how the application provides detailed analysis of cryptocurrencies, including real-time data, historical trends, and market indicators.*

### Crypto Trading Feature
https://github.com/user-attachments/assets/62408efe-a920-400c-8c55-920d99050908

*This video shows how to place cryptocurrency orders through the application interface, with step-by-step instructions on setting up and executing trades.*

## Features

### Detailed Cryptocurrency Analysis
- Real-time market data from Binance API
- Comprehensive price analysis and trends
- Historical trading data visualization
- Market depth and order book information
- 24-hour price statistics and rolling window analysis

### Automated Trading
- Place buy/sell orders directly from the interface
- Test orders before actual execution
- Support for various order types (Limit, Market, etc.)
- Customizable trading parameters

## Technology Stack

- **Backend**: FastAPI, Python, Binance API
- **Frontend**: Streamlit
- **Authentication**: API key-based authentication with Binance
- **Data Processing**: Asynchronous HTTP requests with httpx

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the `api` directory with the following content:
```
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
```

## Getting Started

### Starting the API Server

1. Navigate to the API directory:
```bash
cd api
```

2. Run the main server:
```bash
python main.py
```

This will start the FastAPI server on `http://localhost:8000`.

### Starting the Frontend

1. In a new terminal, navigate to the frontend directory:
```bash
cd frontend
```

2. Run the Streamlit app:
```bash
streamlit run main.py
```

This will start the Streamlit application and open it in your default web browser.

## Usage

1. **Analyzing Cryptocurrency**:
   - Use the interface to select a cryptocurrency symbol (e.g., BTCUSDT, ETHUSDT)
   - View detailed market analysis, including price trends, volume, and market depth
   - Access historical data and technical indicators

2. **Placing Orders**:
   - Select the cryptocurrency you want to trade
   - Choose order type (Limit, Market)
   - Set quantity and price (for Limit orders)
   - Submit the order


## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Security Notes

- Never share your Binance API keys
- For enhanced security, consider using API keys with read-only permissions for analysis-only usage
- The application uses HMAC SHA256 signatures for secure API communication

## License

[Include your license information here]

## Contributing

[Include contribution guidelines if applicable]

## Contact

[Your contact information]
