cat > test_api.py << 'EOF'
import os
from dotenv import load_dotenv
from services.stock_api_service import StockAPIService
from services.stock_service import StockService

# Load environment variables
load_dotenv()

# Test if your API key is loaded
api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
if api_key:
    print(f"✅ API key loaded: {api_key[:10]}...")
else:
    print("❌ API key not found in .env")
    exit()

print("\n" + "="*60)
print("Testing StockAPIService (Raw API)")
print("="*60)

# Test the raw API service
api_service = StockAPIService()

result = api_service.get_stock_price("AAPL")
if result["success"]:
    print(f"✅ Raw API - AAPL: ${result['price']:.2f} ({result['change']:+.2f})")
else:
    print(f"❌ Raw API Error: {result['error']}")

print("\n" + "="*60)
print("Testing StockService (Formatted for TradeBot)")
print("="*60)

# Test the formatted stock service
stock_service = StockService()

# Test price formatting
price_result = stock_service.get_price("AAPL")
if price_result["success"]:
    print("✅ Formatted Price Response:")
    print(price_result["message"])
else:
    print(f"❌ Price Error: {price_result['message']}")

print("\n" + "-" * 40)

# Test analysis formatting
analysis_result = stock_service.get_analysis("AAPL")
if analysis_result["success"]:
    print("✅ Formatted Analysis Response:")
    print(analysis_result["message"])
else:
    print(f"❌ Analysis Error: {analysis_result['message']}")

print("\n" + "="*60)
print("Testing Symbol Extraction")
print("="*60)

test_messages = [
    "What is the price of AAPL?",
    "Buy Tesla stock",
    "Analyze Microsoft",
    "How is GOOGL doing?",
    "Show me NVDA performance"
]

for msg in test_messages:
    symbol = stock_service.extract_symbol_from_message(msg)
    print(f"'{msg}' -> Symbol: {symbol}")
EOF