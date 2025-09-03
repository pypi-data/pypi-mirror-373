########################################################################################################################
# IMPORTS

import logging
from collections.abc import MutableMapping
from typing import Any, Iterator, List, Optional, Type, TypeVar, Union
from urllib.parse import quote_plus

from sqlalchemy import DDL, FrozenResult, Result, Select, SQLColumnExpression, create_engine, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.expression import ClauseElement
from enum import Enum, auto

########################################################################################################################
# CLASSES

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class CommitStrategy(Enum):
    COMMIT_ON_SUCCESS = auto()
    FORCE_COMMIT = auto()


class MockContext:
    def __init__(self, column: SQLColumnExpression) -> None:
        self.current_parameters = {}
        self.current_column = column
        self.connection = None


class AlchemyInterface:
    def __init__(self, config: MutableMapping) -> None:
        self.session: Optional[Session] = None
        if "db" in config:
            self.config = config["db"]
            self.engine = create_engine(self.get_conn_str())
            self.Session = sessionmaker(bind=self.engine)
        else:
            logger.warning("no db section in config")

    def __enter__(self) -> "AlchemyInterface":
        """Enter the runtime context related to this object (starts session)."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the runtime context related to this object (stops session)."""
        should_commit = exc_type is None
        self.stop(commit=should_commit)

    def start(self) -> None:
        """Starts a new SQLAlchemy session manually."""
        if not hasattr(self, "Session"):
            raise AttributeError("Database configuration not initialized. Cannot create session.")
        if self.session is not None:
            raise RuntimeError("Session already active.")
        self.session = self.Session()
        logger.debug("SQLAlchemy session started manually.")

    def stop(self, commit: bool = True) -> None:
        """Stops the manually started SQLAlchemy session."""
        if self.session is None:
            logger.warning("No active session to stop.")
            return

        try:
            if commit:
                logger.debug("Committing SQLAlchemy session before stopping.")
                self.session.commit()
            else:
                logger.debug("Rolling back SQLAlchemy session before stopping.")
                self.session.rollback()
        except Exception as e:
            logger.error(f"Exception during session commit/rollback on stop: {e}", exc_info=True)
            try:
                self.session.rollback()
            except Exception as rb_exc:
                logger.error(f"Exception during secondary rollback attempt on stop: {rb_exc}", exc_info=True)
            raise
        finally:
            logger.debug("Closing SQLAlchemy session.")
            self.session.close()
            self.session = None

    def get_conn_str(self):
        return (
            f"{self.config['engine']}://"
            f"{self.config['user']}:{quote_plus(self.config['password'])}"
            f"@{self.config['host']}:{self.config['port']}"
            f"/{self.config['database']}"
        )

    @staticmethod
    def get_schema_from_table(table: Type[ModelType]) -> str:
        schema = "public"

        if isinstance(table.__table_args__, tuple):
            for table_arg in table.__table_args__:
                if isinstance(table_arg, dict) and "schema" in table_arg:
                    schema = table_arg["schema"]

        elif isinstance(table.__table_args__, dict) and "schema" in table.__table_args__:
            schema = table.__table_args__["schema"]

        if schema == "public":
            logger.warning(f"no database schema provided, switching to {schema}...")

        return schema

    def create_tables(self, tables: List[Type[ModelType]]) -> None:
        for table in tables:
            schema = self.get_schema_from_table(table)

            with self.engine.connect() as conn:
                conn.execute(DDL(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                conn.commit()

                if hasattr(table, "is_view") and table.is_view:
                    if not conn.dialect.has_table(conn, table.__tablename__, schema=schema):
                        logger.info(f"creating view {table.__tablename__}...")
                        table.create_view(conn)
                        conn.commit()
                    else:
                        logger.info(f"view {table.__tablename__} already exists")
                else:
                    if not conn.dialect.has_table(conn, table.__tablename__, schema=schema):
                        logger.info(f"creating table {table.__tablename__}...")
                        table.__table__.create(conn)
                        conn.commit()
                    else:
                        logger.info(f"table {table.__tablename__} already exists")

    def drop_tables(self, tables: List[Type[ModelType]]) -> None:
        for table in tables:
            schema = self.get_schema_from_table(table)

            with self.engine.connect() as conn:
                if hasattr(table, "is_view") and table.is_view:
                    if conn.dialect.has_table(conn, table.__tablename__, schema=schema):
                        logger.info(f"dropping view {table.__tablename__}...")
                        conn.execute(DDL(f"DROP VIEW {schema}.{table.__tablename__} CASCADE"))
                        conn.commit()
                else:
                    if conn.dialect.has_table(conn, table.__tablename__, schema=schema):
                        logger.info(f"dropping table {table.__tablename__}...")
                        conn.execute(DDL(f"DROP TABLE {schema}.{table.__tablename__} CASCADE"))
                        conn.commit()

    def reset_db(self, tables: List[Type[ModelType]], drop: bool = False) -> None:
        if drop:
            self.drop_tables(tables)

        self.create_tables(tables)

    def reset_column(self, query_results: List[Result[Any]], column_name: str) -> None:
        """
        Reset a column to its default value for a list of query results.

        Args:
            query_results: List of query results to update
            column_name: Name of the column to reset
        """
        if self.session is None:
            raise RuntimeError("Session not active. Use 'with AlchemyInterface(...):' or call start()")

        if not query_results:
            logger.warning("No objects to reset column for.")
            return

        first_obj = query_results[0]
        model_class = first_obj.__class__
        table = model_class.__table__

        if column_name not in table.columns:
            logger.warning(f"Column {column_name} does not exist in table {table.name}.")
            return

        column = table.columns[column_name]

        # Determine the default value to use
        if column.server_default is not None:
            default_value = text("DEFAULT")
        elif column.default is not None:
            default_value = column.default.arg
            if callable(default_value):
                default_value = default_value(MockContext(column))
        else:
            raise ValueError(f"Column '{column_name}' doesn't have a default value defined.")

        query_results.update({column_name: default_value}, synchronize_session=False)

    def insert_alchemy_obj(self, alchemy_obj: ModelType, silent: bool = False) -> bool:
        if self.session is None:
            raise RuntimeError("Session not active. Use 'with AlchemyInterface(...):' or call start()")

        try:
            # Use a savepoint (nested transaction)
            with self.session.begin_nested():
                if not silent:
                    logger.info(f"adding {alchemy_obj}...")
                self.session.add(alchemy_obj)
        except IntegrityError:
            # Rollback is handled automatically by begin_nested() context manager on error
            if not silent:
                logger.info(f"{alchemy_obj} already in db (savepoint rolled back)")
            # Do not re-raise, allow outer transaction/loop to continue
            return False

        return True

    def upsert_alchemy_obj(self, alchemy_obj: ModelType, index_elements: List[str], silent: bool = False) -> bool:
        if self.session is None:
            raise RuntimeError("Session not active. Use 'with AlchemyInterface(...):' or call start()")

        if not silent:
            logger.info(f"upserting {alchemy_obj}")

        table = alchemy_obj.__table__
        primary_keys = list(col.name for col in table.primary_key.columns.values())

        # Build the dictionary for the INSERT values
        insert_values = {
            col.name: getattr(alchemy_obj, col.name)
            for col in table.columns
            if getattr(alchemy_obj, col.name) is not None  # Include all non-None values for insert
        }

        # Build the dictionary for the UPDATE set clause
        # Start with values from the object, excluding primary keys
        update_set_values = {
            col.name: val
            for col in table.columns
            if col.name not in primary_keys and (val := getattr(alchemy_obj, col.name)) is not None
        }

        # Add columns with SQL-based onupdate values explicitly to the set clause
        for column in table.columns:
            actual_sql_expression = None
            if column.onupdate is not None:
                if hasattr(column.onupdate, "arg") and isinstance(column.onupdate.arg, ClauseElement):
                    # This handles wrappers like ColumnElementColumnDefault,
                    # where the actual SQL expression is in the .arg attribute.
                    actual_sql_expression = column.onupdate.arg
                elif isinstance(column.onupdate, ClauseElement):
                    # This handles cases where onupdate might be a direct SQL expression.
                    actual_sql_expression = column.onupdate

            if actual_sql_expression is not None:
                update_set_values[column.name] = actual_sql_expression

        statement = (
            insert(table)
            .values(insert_values)
            .on_conflict_do_update(index_elements=index_elements, set_=update_set_values)
        )

        try:
            # Use a savepoint (nested transaction)
            with self.session.begin_nested():
                self.session.execute(statement)
        except IntegrityError:
            # Rollback is handled automatically by begin_nested() context manager on error
            if not silent:
                logger.info(f"could not upsert {alchemy_obj} (savepoint rolled back)")
            # Do not re-raise, allow outer transaction/loop to continue
            return False

        return True

    def windowed_query(
        self,
        stmt: Select[Any],
        order_by: List[SQLColumnExpression[Any]],
        windowsize: int,
        commit_strategy: Union[CommitStrategy, str] = CommitStrategy.COMMIT_ON_SUCCESS,
    ) -> Iterator[Result[Any]]:
        """
        Executes a windowed query, fetching each window in a separate, short-lived session.

        Args:
            stmt: The SQL select statement to execute.
            order_by: The columns to use for ordering.
            windowsize: The number of rows to fetch in each window.
            commit_strategy: The strategy to use for committing the session after each window.
                             Defaults to `CommitStrategy.COMMIT_ON_SUCCESS`.

        Returns:
            An iterator of Result objects, each containing a window of data.
            The session used to fetch the Result is closed immediately after yielding.

        More info: https://github.com/sqlalchemy/sqlalchemy/wiki/RangeQuery-and-WindowedRangeQuery
        """
        # Parameter mapping
        if isinstance(commit_strategy, str):
            commit_strategy = CommitStrategy[commit_strategy.upper()]

        # Find id column in stmt
        if not any(column.get("entity").id for column in stmt.column_descriptions):
            raise Exception("Column 'id' not found in any entity of the query.")
        id_column = stmt.column_descriptions[0]["entity"].id

        last_id = 0
        while True:
            session_active = False
            commit_needed = False
            try:
                self.start()
                session_active = True

                # Filter on row_number in the outer query
                current_query = stmt.where(id_column > last_id).order_by(order_by[0], *order_by[1:]).limit(windowsize)
                result = self.session.execute(current_query)

                # Create a FrozenResult to allow peeking at the data without consuming
                frozen_result: FrozenResult = result.freeze()
                chunk = frozen_result().all()

                if not chunk:
                    break

                # Update for next iteration
                last_id = chunk[-1].id

                # Create a new Result object from the FrozenResult
                yield_result = frozen_result()

                yield yield_result
                commit_needed = True

            finally:
                if session_active and self.session:
                    if commit_strategy == CommitStrategy.FORCE_COMMIT:
                        # For forced commit, always attempt to commit.
                        # The self.stop() method already handles potential exceptions during commit/rollback.
                        self.stop(commit=True)
                    elif commit_strategy == CommitStrategy.COMMIT_ON_SUCCESS:
                        # Commit only if no exception occurred before yielding the result.
                        self.stop(commit=commit_needed)
                    else:
                        # Fallback or error for unknown strategy, though type hinting should prevent this.
                        # For safety, default to rollback.
                        logger.warning(f"Unknown commit strategy: {commit_strategy}. Defaulting to rollback.")
                        self.stop(commit=False)
