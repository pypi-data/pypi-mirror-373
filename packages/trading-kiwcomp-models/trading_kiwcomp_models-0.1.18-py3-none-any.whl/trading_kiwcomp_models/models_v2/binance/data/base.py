# from sqlalchemy.orm import DeclarativeBase
# # class Base(DeclarativeBase):
# #     pass

# # Abstract base for ExchangeInfo
# class ExchangeInfoSymbol(DeclarativeBase):
#     pass

# class BinanceKline(DeclarativeBase):
#     pass
try:
    from sqlalchemy.orm import DeclarativeBase

    class ExchangeInfoSymbol(DeclarativeBase):
        pass

    class BinanceKline(DeclarativeBase):
        pass

except ImportError:
    from sqlalchemy.ext.declarative import declarative_base

    ExchangeInfoSymbol = declarative_base()
    BinanceKline = declarative_base()