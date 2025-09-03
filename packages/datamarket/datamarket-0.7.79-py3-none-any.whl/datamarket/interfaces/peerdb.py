########################################################################################################################
# IMPORTS

import base64
import logging
import re
import time

import boto3
import clickhouse_driver
import requests
from requests.exceptions import HTTPError
from sqlalchemy import text
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential

from .alchemy import AlchemyInterface

########################################################################################################################
# EXCEPTIONS


class DatabaseNotConnectedError(Exception):
    """Custom error for when database is not connected."""

    pass


########################################################################################################################
# CLASSES

logger = logging.getLogger(__name__)


class PostgresPeer:
    def __init__(self, config):
        if "db" in config:
            self.config = config["db"]
            self.alchemy_interface = AlchemyInterface(config)
            self.engine = self.alchemy_interface.engine
        else:
            logger.warning("no db section in config")

    def create_user(self, user, password):
        database = self.config["database"]

        logger.info(f"Creating PostgreSQL user '{user}' for database: {self.config['database']}")

        with self.engine.connect() as conn:
            conn.execute(
                text(f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{user}') THEN
                        CREATE USER "{user}" WITH PASSWORD '{password}';
                        ALTER USER "{user}" REPLICATION;
                        GRANT CREATE ON DATABASE {database} TO "{user}";
                    END IF;
                END
                $$;
                """)
            )
            conn.commit()
        logger.info(f"PostgreSQL user '{user}' created or already exists")

    def grant_permissions(self, schema_name, user):
        logger.info(f"Granting permissions for schema '{schema_name}' to '{user}'")

        with self.engine.connect() as conn:
            conn.execute(
                text(f"""
                GRANT USAGE ON SCHEMA "{schema_name}" TO "{user}";
                GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA "{schema_name}" TO "{user}";
                ALTER DEFAULT PRIVILEGES IN SCHEMA "{schema_name}" GRANT ALL PRIVILEGES ON TABLES TO "{user}";
                """)
            )
            conn.commit()
        logger.info(f"Permissions granted for schema '{schema_name}' to '{user}'")

    def create_publication(self, schema_name, table_names):
        logger.info(f"Creating publication '{schema_name}_peerdb' for schema: {schema_name}")
        with self.engine.connect() as conn:
            conn.execute(text(f"DROP PUBLICATION IF EXISTS {schema_name}_peerdb"))

            table_list = []
            for table in table_names:
                full_table_name = f'"{schema_name}"."{table}"'

                # Check current replica identity
                query = text("""
                    SELECT CASE c.relreplident
                             WHEN 'd' THEN 'DEFAULT'
                             WHEN 'n' THEN 'NOTHING'
                             WHEN 'f' THEN 'FULL'
                             WHEN 'i' THEN 'INDEX'
                           END AS replica_identity
                    FROM pg_class c
                    JOIN pg_namespace n ON c.relnamespace = n.oid
                    WHERE c.relname = :table_name
                      AND n.nspname = :schema_name;
                """)
                result = conn.execute(query, {"table_name": table, "schema_name": schema_name}).scalar_one_or_none()

                if result != "FULL":
                    logger.info(f"Setting REPLICA IDENTITY FULL for table: {full_table_name}")
                    conn.execute(text(f"ALTER TABLE {full_table_name} REPLICA IDENTITY FULL;"))
                else:
                    logger.info(f"REPLICA IDENTITY for table {full_table_name} is already FULL. Skipping ALTER TABLE.")

                table_list.append(full_table_name)

            table_list_str = ", ".join(table_list)
            conn.execute(
                text(f"""
                CREATE PUBLICATION {schema_name}_peerdb FOR TABLE {table_list_str};
                """)
            )
            conn.commit()
        logger.info(f"Publication '{schema_name}_peerdb' created successfully")

    def create_tables(self, schema_tables, drop=False):
        logger.info(f"Creating tables in database: {self.config['database']}")
        self.alchemy_interface.reset_db(schema_tables, drop)
        logger.info(f"Tables {'dropped and ' if drop else ''}created successfully")

    def drop_replication_slot(self, schema_name):
        logger.info(f"Checking and dropping replication slot for schema: {schema_name}")
        slot_name = f"peerflow_slot_{schema_name}"

        with self.engine.connect() as conn:
            conn.execute(
                text("""
                SELECT pg_drop_replication_slot(:slot_name)
                WHERE EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = :slot_name)
                """),
                {"slot_name": slot_name},
            )
            conn.commit()
            logger.info(f"Replication slot '{slot_name}' dropped if it existed")


class ClickhousePeer:
    def __init__(self, config):
        if "clickhouse" in config:
            self.config = config["clickhouse"]
            self.credentials = {key: self.config[key] for key in ["user", "password", "host", "port"]}

        else:
            logger.warning("no clickhouse section in config")

    def connect(self, database):
        if not database:
            return

        self.ensure_database_exists(database)
        self.config["database"] = self.credentials["database"] = database
        self.client = clickhouse_driver.Client(**self.credentials)

    def _check_connection(self):
        if self.client is None:
            raise DatabaseNotConnectedError("Database not connected. Call connect() method first.")

    def ensure_database_exists(self, database):
        logger.info(f"Checking if database '{database}' exists in Clickhouse")
        temp_client = clickhouse_driver.Client(**self.credentials)
        databases = temp_client.execute("SHOW DATABASES")
        if database not in [db[0] for db in databases]:
            logger.info(f"Creating database '{database}'")
            temp_client.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        temp_client.disconnect()

    def delete_existing_tables(self, table_names):
        self._check_connection()
        logger.info(f"Deleting existing tables in Clickhouse for database: {self.config['database']}")

        all_tables = self.client.execute("SHOW TABLES")
        all_tables = [table[0] for table in all_tables]

        # Delete tables containing "peerdb" in their names
        for table in all_tables:
            if "peerdb" in table.lower():
                self.client.execute(f"DROP TABLE IF EXISTS {table}")
                logger.info(f"Deleted table: {table}")

        # Delete tables passed through run_automation and their "_resync" variants
        for table in table_names:
            if table in all_tables:
                self.client.execute(f"DROP TABLE IF EXISTS {table}")
                logger.info(f"Deleted table: {table}")

            resync_table = f"{table}_resync"
            if resync_table in all_tables:
                self.client.execute(f"DROP TABLE IF EXISTS {resync_table}")
                logger.info(f"Deleted table: {resync_table}")

        logger.info("Finished deleting existing tables in Clickhouse")

    def create_row_policies(self, schema_name, table_names):
        self._check_connection()
        logger.info(f"Creating row policies for schema: {schema_name}")
        for table_name in table_names:
            policy_name = "non_deleted"
            query = f"""
            CREATE ROW POLICY IF NOT EXISTS {policy_name} ON {schema_name}.{table_name}
            FOR SELECT USING _peerdb_is_deleted = 0
            """
            self.client.execute(query)
            logger.info(f"Created row policy '{policy_name}' for table '{table_name}'")

    def execute_sql_file(self, file_path):
        self._check_connection()
        try:
            with file_path.open("r") as sql_file:
                sql_content = sql_file.read()
                logger.info(f"Executing SQL from file: {file_path}")

                sql_statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

                for statement in sql_statements:
                    self.client.execute(statement)
                    logger.info(f"Successfully executed SQL statement: {statement}")

        except Exception as e:
            logger.error(f"Error executing SQL from file {file_path}: {str(e)}")

    def teardown_from_sql_folder(self, sql_folder):
        logger.info("Performing ClickHouse teardown")
        self._process_sql_files(sql_folder, teardown=True)
        logger.info("ClickHouse teardown completed")

    def initialize_from_sql_folder(self, sql_folder):
        logger.info(f"Initializing Clickhouse database from SQL files in folder: {sql_folder}")
        self._process_sql_files(sql_folder)
        logger.info("Finished initializing Clickhouse database from SQL files")

    def _process_sql_files(self, sql_folder, teardown=False):
        if not sql_folder.exists():
            logger.error(f"SQL initialization folder does not exist: {sql_folder}")
            return

        all_dirs = [sql_folder] + [d for d in sql_folder.rglob("*") if d.is_dir()]
        sorted_dirs = sorted(all_dirs)

        for directory in sorted_dirs:
            sql_files = self._filter_sql_files(directory, teardown)

            for file_path in sql_files:
                self.execute_sql_file(file_path)

    def _filter_sql_files(self, directory, teardown):
        all_sql_files = directory.glob("*.sql")
        return sorted(f for f in all_sql_files if ("teardown" in f.name.lower()) == teardown)


class TransientS3:
    def __init__(self, config):
        if "peerdb-s3" in config:
            self.config = config["peerdb-s3"]
            self.bucket_name = self.config["bucket"]
            self.session = boto3.Session(profile_name=self.config["profile"])
            self.s3_client = self.session.client("s3")
            self.credentials = self.session.get_credentials()
            self.access_key = self.credentials.access_key
            self.secret_key = self.credentials.secret_key
            self.region_name = self.session.region_name
            self.endpoint_url = self.s3_client.meta.endpoint_url
        else:
            logger.warning("no peerdb-s3 section in config")

    def delete_paths_with_schema(self, schema_name):
        logger.info(f"Deleting paths containing '{schema_name}' from S3")

        paginator = self.s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self.bucket_name, Delimiter="/")

        for page in pages:
            if "CommonPrefixes" in page:
                for prefix in page["CommonPrefixes"]:
                    folder = prefix["Prefix"]
                    if schema_name in folder:
                        self._delete_folder_contents(folder)

        logger.info(f"Deleted paths containing '{schema_name}' from S3")

    def _delete_folder_contents(self, folder):
        logger.info(f"Deleting contents of folder: {folder}")

        paginator = self.s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=folder)

        delete_us = dict(Objects=[])
        for page in pages:
            if "Contents" in page:
                for obj in page["Contents"]:
                    delete_us["Objects"].append(dict(Key=obj["Key"]))

                    # AWS limits to deleting 1000 objects at a time
                    if len(delete_us["Objects"]) >= 1000:
                        self.s3_client.delete_objects(Bucket=self.bucket_name, Delete=delete_us)
                        delete_us = dict(Objects=[])

        if len(delete_us["Objects"]):
            self.s3_client.delete_objects(Bucket=self.bucket_name, Delete=delete_us)

        logger.info(f"Deleted contents of folder: {folder}")


class PeerDBInterface:
    def __init__(self, config):
        if "peerdb" in config:
            self.config = config["peerdb"]
            self.docker_host_mapping = self.config.get("docker_host_mapping")
        else:
            logger.warning("no peerdb section in config")

        self.source = PostgresPeer(config)
        self.transient_s3 = TransientS3(config)
        self.destination = ClickhousePeer(config)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def _make_api_request(self, endpoint, payload):
        url = f"http://{self.config['host']}:{self.config['port']}/api/{endpoint}"
        password = self.config["password"]
        credentials = f":{password}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        headers = {"Authorization": f"Basic {encoded_credentials}", "Content-Type": "application/json"}

        logger.debug(f"Making API request to PeerDB endpoint: {endpoint}")
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            response = r.json()
            r.raise_for_status()
            logger.debug(f"API request to {endpoint} completed successfully")
            return response
        except HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            logger.error(f"Response JSON: {r.json() if 'r' in locals() else 'N/A'}")

            if "no rows in result set" in response.get("message", ""):
                return {"currentFlowState": "STATUS_UNKNOWN"}

            raise

    def _resolve_host_mapping(self, host):
        """
        Resolves host mapping for Docker environments.
        If host is localhost/127.0.0.1 and docker_host_mapping is configured,
        returns the mapped host, otherwise returns original host.
        """
        if not self.docker_host_mapping or not host:
            return host

        if host in ["localhost", "127.0.0.1"]:
            logger.debug(f"Mapping host {host} to {self.docker_host_mapping} for Docker environment")
            return self.docker_host_mapping

        url_pattern = r"(localhost|127\.0\.0\.1)"
        match = re.search(url_pattern, host)
        if match:
            original_host = match.group(1)
            mapped_host = self._resolve_host_mapping(original_host)
            return host.replace(original_host, mapped_host)

        return host

    def create_postgres_peer(self):
        logger.info(f"Creating Postgres peer for database: {self.source.config['database']}")
        payload = {
            "peer": {
                "name": self.source.config["database"],
                "type": 3,
                "postgres_config": {
                    "host": self._resolve_host_mapping(self.source.config["host"]),
                    "port": int(self.source.config["admin_port"]),
                    "user": self.config["user"],
                    "password": self.config["password"],
                    "database": self.source.config["database"],
                },
            },
            "allow_update": True,
        }

        response = self._make_api_request("v1/peers/create", payload)
        if response.get("status") == "FAILED":
            raise Exception(f"Failed to create Postgres peer: {response.get('message', 'Unknown error')}")

        logger.info(f"Postgres peer for database '{self.source.config['database']}' created successfully")

    def create_clickhouse_peer(self, schema_name):
        logger.info(f"Creating Clickhouse peer for schema: {schema_name}")
        payload = {
            "peer": {
                "name": f"{schema_name}",
                "type": 8,
                "clickhouse_config": {
                    "host": self._resolve_host_mapping(self.destination.config["host"]),
                    "port": int(self.destination.config["port"]),
                    "user": self.destination.config["user"],
                    "password": self.destination.config["password"],
                    "database": schema_name,
                    "disable_tls": True,
                    "s3_path": f"s3://{self.transient_s3.bucket_name}",
                    "access_key_id": self.transient_s3.access_key,
                    "secret_access_key": self.transient_s3.secret_key,
                    "region": self.transient_s3.region_name,
                    "endpoint": self._resolve_host_mapping(self.transient_s3.endpoint_url),
                },
            },
            "allow_update": True,
        }

        response = self._make_api_request("v1/peers/create", payload)
        if response.get("status") == "FAILED":
            raise Exception(f"Failed to create Clickhouse peer: {response.get('message', 'Unknown error')}")

        logger.info(f"Clickhouse peer for schema '{schema_name}' created successfully")

    def check_mirror_status(self, schema_name):
        current_state = "STATUS_UNKNOWN"
        try:
            payload = {"flowJobName": schema_name, "includeFlowInfo": False}
            response = self._make_api_request("v1/mirrors/status", payload)
            current_state = response.get("currentFlowState")
        except Exception as e:
            logger.debug(f"Error checking mirror status for schema '{schema_name}': {str(e)}")
        return current_state

    def drop_mirror(self, schema_name):
        logger.info(f"Dropping mirror for schema: {schema_name}")

        payload = {"flowJobName": f"{schema_name}", "requestedFlowState": "STATUS_TERMINATED"}

        mirror_status = self.check_mirror_status(schema_name)
        if mirror_status == "STATUS_UNKNOWN":
            logger.info(f"Mirror for schema '{schema_name}' does not exist, no need to drop.")
            return

        response = self._make_api_request("v1/mirrors/state_change", payload)
        if not bool(response.get("ok", "true")) or int(response.get("code", 0)) == 2:
            raise Exception(
                f"Failed to drop mirror for schema '{schema_name}': {response.get('errorMessage', response.get('message', 'Unknown error'))}"
            )

        logger.info(f"Mirror for schema '{schema_name}' dropped successfully")

    def wait_for_running_mirror(self, schema_name, max_attempts=360, sleep_interval=10):
        logger.info(f"Waiting for mirror status to be 'STATUS_RUNNING' for schema: {schema_name}")
        attempt = 0
        while attempt < max_attempts:
            current_state = self.check_mirror_status(schema_name)

            if current_state == "STATUS_RUNNING":
                logger.info(f"Mirror status for schema '{schema_name}' is now: {current_state}")
                return current_state

            attempt += 1
            logger.info(f"Status is '{current_state}'. Waiting {sleep_interval} seconds before next check.")
            time.sleep(sleep_interval)

        logger.warning(f"Mirror status check timed out for schema: {schema_name}")
        return None

    def pre_init(self, schema_name, table_names, clickhouse_sql_path, resync, hard_resync):
        logger.info("Running pre-init operations.")
        if resync:
            self.drop_mirror(schema_name)
            self.transient_s3.delete_paths_with_schema(schema_name)
            self.destination.teardown_from_sql_folder(clickhouse_sql_path)
            self.source.drop_replication_slot(schema_name)
            if hard_resync:
                self.destination.delete_existing_tables(table_names)
        logger.info("Pre-init operations completed.")

    def post_init(self, schema_name, table_names, clickhouse_sql_path, resync, hard_resync):
        logger.info("Running post-init operations.")
        self.destination.create_row_policies(schema_name, table_names)
        if resync:
            self.destination.initialize_from_sql_folder(clickhouse_sql_path)
        logger.info("Post-init operations completed.")

    def create_mirror(self, schema_name, table_names, resync, hard_resync):
        logger.info(f"Creating mirror for schema: {schema_name}")

        table_mappings = [
            {"source_table_identifier": f"{schema_name}.{table}", "destination_table_identifier": f"{table}"}
            for table in table_names
        ]

        payload = {
            "connection_configs": {
                "flow_job_name": f"{schema_name}",
                "source_name": self.source.config["database"],
                "destination_name": f"{schema_name}",
                "table_mappings": table_mappings,
                "max_batch_size": 1000000,
                "idle_timeout_seconds": 10,
                "publication_name": f"{schema_name}_peerdb",
                "do_initial_snapshot": True,
                "snapshot_num_rows_per_partition": 1000000,
                "snapshot_max_parallel_workers": 1,
                "snapshot_num_tables_in_parallel": 1,
                "resync": resync and not hard_resync,
                "initial_snapshot_only": False,
                "soft_delete_col_name": "_peerdb_is_deleted",
                "synced_at_col_name": "_peerdb_synced_at",
            }
        }

        response = self._make_api_request("v1/flows/cdc/create", payload)
        if not bool(response.get("ok", "true")) or int(response.get("code", 0)) == 2:
            raise Exception(
                f"Failed to create mirror for schema '{schema_name}': {response.get('errorMessage', response.get('message', 'Unknown error'))}"
            )

        mirror_status = self.wait_for_running_mirror(schema_name)
        if mirror_status:
            logger.info(f"Mirror creation for schema '{schema_name}' completed successfully")
        else:
            logger.warning(f"Failed to confirm mirror status change for schema: {schema_name}")

    def run_automation(
        self,
        schema_name,
        schema_tables,
        drop=False,
        sync=False,
        resync=False,
        hard_resync=False,
        clickhouse_sql_path=None,
    ):
        logger.info(f"Starting automation for schema: {schema_name}")

        base_tables = [table for table, _ in schema_tables]
        mirror_tablenames = [table.__tablename__ for table, should_replicate in schema_tables if should_replicate]

        self.source.create_tables(base_tables, drop)
        if not (sync or resync):
            return

        peerdb_user = self.config["user"]
        peerdb_pwd = self.config["password"]

        self.source.create_user(peerdb_user, peerdb_pwd)
        self.source.grant_permissions(schema_name, peerdb_user)
        self.source.create_publication(schema_name, mirror_tablenames)
        self.destination.connect(schema_name)
        self.create_postgres_peer()
        self.create_clickhouse_peer(schema_name)
        self.pre_init(schema_name, mirror_tablenames, clickhouse_sql_path, resync, hard_resync)
        self.create_mirror(schema_name, mirror_tablenames, resync, hard_resync)
        self.post_init(schema_name, mirror_tablenames, clickhouse_sql_path, resync, hard_resync)

        logger.info(f"Automation completed successfully for schema: {schema_name}")
