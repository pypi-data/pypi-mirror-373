from ...data import Base
from sqlalchemy import Column, Integer, String, VARCHAR, DateTime, Float


class ASSET_UNIVERSE_TS(Base):
    __tablename__ = 'ASSET_UNIVERSE_TS'
    __table_args__ = {"schema": "ANALYTICS"}
    
    DATE_OF_DATA = Column(DateTime, primary_key=True)
    MODEL = Column(String(80), primary_key=True)
    BARRA_ID = Column(String(80), primary_key=True)
    SECURITY_NAME = Column(String(80))
    SEDOL = Column(String(80))
    CUSIP = Column(String(80))
    ISIN = Column(String(80))
    RIC = Column(String(80))
    LOCALID = Column(String(80))
    MIC_CODE = Column(String(80))
    COUNTRY_OF_QUOTATION = Column(String(80))
    COUNTRY_OF_EXPOSURE = Column(String(80))
    IS_ESTIMATION_UNIVERSE = Column(String(80))


class ASSET_EXPOSURES_TS(Base):
    __tablename__ = 'ASSET_EXPOSURES_TS'
    __table_args__ = {"schema": "ANALYTICS"}
    
    DATE_OF_DATA = Column(DateTime, primary_key=True)
    MODEL = Column(String(80))
    BARRA_ID = Column(String(80), primary_key=True)
    FACTOR_GROUP = Column(String(80))
    FACTOR = Column(String(80))
    FACTOR_NAME = Column(String(80))
    FACTOR_NUM = Column(String(80))
    EXPOSURE = Column(Float)

class FACTOR_COVARIANCE_TS(Base):
    __tablename__ = 'FACTOR_COVARIANCE_TS'
    __table_args__ = {"schema": "ANALYTICS"}
    
    DATE_OF_DATA = Column(DateTime, primary_key=True)
    MODEL = Column(String(80))
    FACTOR = Column(String(80), primary_key=True)
    OTHER_FACTOR = Column(String(80))
    COVARIANCE = Column(Float)