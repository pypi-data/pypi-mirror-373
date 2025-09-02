import logging
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker

from .. import settings
from ..data import Base


class QuantSnowflakeDataEngine:

    def __init__(self, engine):
        settings.setup_logging()
        self.logger = logging.getLogger(__name__)
        session = sessionmaker()
        self.connection = engine.connect()
        self.session = session(bind=engine)
        self.meta = MetaData(self.connection)
        Base.metadata.create_all(self.connection)