# from sqlalchemy.orm import DeclarativeBase
# class StreamKline(DeclarativeBase):
#     pass

# class MarkPriceUpdate(DeclarativeBase):
#     pass

try:
    from sqlalchemy.orm import DeclarativeBase

   
    class StreamKline(DeclarativeBase):
        pass

    class MarkPriceUpdate(DeclarativeBase):
        pass

except ImportError:
    from sqlalchemy.ext.declarative import declarative_base

    StreamKline = declarative_base()
    MarkPriceUpdate = declarative_base()