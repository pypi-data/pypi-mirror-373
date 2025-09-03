########################################################################################################################
# IMPORTS

from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# CLASSES

Base = declarative_base()

class View(Base):
    __abstract__ = True
    is_view = True

    @classmethod
    def create_view(cls, conn):
        query = """
            -- Your SQL query goes here
        """
        conn.execute(f"""
            CREATE OR REPLACE VIEW {cls.__tablename__} AS {query}
        """)