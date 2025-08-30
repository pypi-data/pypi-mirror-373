from sqlalchemy import create_engine
from binance.data.base import ExchangeInfoSymbol
from binance.stream.base import StreamKline
from binance.stream.base import MarkPriceUpdate
from urllib.parse import quote_plus
import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from trading_core.connector.postgres import PostgresqlDBConnector

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

# ✅ test connection via psycopg2
with PostgresqlDBConnector(DB_NAME, DB_PORT, DB_HOST, DB_USER, DB_PASSWORD) as conn:
    conn.execute_query("SELECT 1;")
    print("✅ psycopg2 connection OK")

# ✅ create tables via SQLAlchemy
for base in [ExchangeInfoSymbol, StreamKline, MarkPriceUpdate]:
    base.metadata.create_all(engine)
