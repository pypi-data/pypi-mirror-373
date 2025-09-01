from binance.data.base import BinanceKline
from binance.data.BinanceSpotKline import BinanceSpotKlineTable
from binance.data.BinanceFuturesUSDTKline import BinanceFuturesUSDTKlineTable
from binance.data.BinanceFuturesCOINMKline import BinanceFuturesCOINMKlineTable

from binance.data.base import ExchangeInfoSymbol
from binance.data.BinanceSpotExchangeInfoSymbol import BinanceSpotExchangeInfoSymbolTable
from binance.data.BinanceFuturesUSDTExchangeInfoSymbol import BinanceFuturesUSDTExchangeInfoSymbolTable
from binance.data.BinanceFuturesCOINMExchangeInfoSymbol import BinanceFuturesCOINMExchangeInfoSymbolTable

from binance.stream.base import StreamKline
from binance.stream.BinanceStreamFuturesCOINMKline import BinanceStreamFuturesCOINMKlineTable
from binance.stream.BinanceStreamFuturesUSDTKline import BinanceStreamFuturesUSDTKlineTable
from binance.stream.BinanceStreamSpotKline import BinanceStreamSpotKlineTable

from binance.stream.base import MarkPriceUpdate
from binance.stream.BinanceStreamFuturesCOINMMarkPriceUpdate import BinanceStreamFuturesCOINMMarkPriceUpdateTable
from binance.stream.BinanceStreamFuturesUSDTMarkPriceUpdate import BinanceStreamFuturesUSDTMarkPriceUpdateTable

from sqlalchemy import create_engine
from urllib.parse import quote_plus
import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

DB_USER = "kiwadmin"
DB_PASSWORD = "kiwpass@1689"
DB_HOST = "pgdev.internal.kiwcomp.com"
DB_PORT = "5432"
DB_NAME = "testdb"

# ✅ encode password
password_encoded = quote_plus(DB_PASSWORD)

# ✅ SQLAlchemy engine
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)

ExchangeInfoSymbol.metadata.create_all(engine)
BinanceKline.metadata.create_all(engine)
StreamKline.metadata.create_all(engine)
MarkPriceUpdate.metadata.create_all(engine)