import logging

import psycopg2
from psycopg2 import sql

from ms_salesforce_api.salesforce.api.opportunity.constants import (
    DEFAULT_DELETE_ALL_OPPORTUNITY_TABLE,
    DEFAULT_DELETE_OPPORTUNITY_LINE_ITEM_TABLE,
    DEFAULT_POSTGRES_DATABASE_SCHEMAS_MAP,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CloudSQL:
    """
    Connect with a Postgres Database with the given
    host name, database name, username, and password.

    Args:
        host (str): The host name for the Postgres database.
        user (str): The username for accessing the database.
        password (str): The password for accessing the database.
        dbname (str): The name of the database.
    """

    BATCH_SIZE = 1

    def __init__(self, host, user, password, dbname, debug_mode=False):
        self.debug_mode = debug_mode

        self.check_and_create_database(host, user, password, dbname)

        self.connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=dbname,
        )

        self.check_and_create_tables()

    def check_and_create_database(self, host, user, password, database):
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname="postgres",
        )

        cursor = conn.cursor()

        check_db_query = f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{database}'"  # noqa: E501

        cursor.execute(check_db_query)

        result = cursor.fetchone()

        if result is None:
            logging.info(f"Creating database '{database}'...")
            create_db_query = f"CREATE DATABASE {database}"
            cursor.execute("COMMIT")
            cursor.execute(create_db_query)
            logging.info(f"Database '{database}' created.")

        conn.commit()

        cursor.close()
        conn.close()

    def check_and_create_tables(self):
        cursor = self.connection.cursor()

        for db_schema in DEFAULT_POSTGRES_DATABASE_SCHEMAS_MAP:
            table_name = db_schema["db_name"]
            # Check if table exists
            check_table_query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name.lower()}')"  # noqa: E501
            cursor.execute(check_table_query)

            result = cursor.fetchone()

            if not result[0]:
                cursor.execute(db_schema["query"])
                logging.info(f"Table '{table_name}' created.")

        self.connection.commit()

        cursor.close()

    def delete_all_rows(self):
        cursor = self.connection.cursor()
        logging.info("Deleting all opportunities tables...")

        cursor.execute(DEFAULT_DELETE_OPPORTUNITY_LINE_ITEM_TABLE)
        cursor.execute(DEFAULT_DELETE_ALL_OPPORTUNITY_TABLE)

        self.connection.commit()

        cursor.close()

    def export_data(self, opportunities):
        with self.connection.cursor() as cursor:
            opportunity_batches = self._create_batches(
                opportunities,
                self.BATCH_SIZE,
            )
            for opportunity_batch in opportunity_batches:
                self._insert_opportunities_batch(cursor, opportunity_batch)
                opportunity_line_items = []

                for opportunity in opportunity_batch:
                    opportunity_line_items.extend(
                        opportunity.get("opportunity_line_items", [])
                    )

                if opportunity_line_items:
                    self._insert_opportunity_lines_batch(
                        cursor, opportunity_line_items
                    )

        self.connection.commit()

    def _create_batches(self, data, batch_size):
        return [
            data[i : i + batch_size]  # noqa: E203
            for i in range(0, len(data), batch_size)
        ]

    def _insert_opportunities_batch(self, cursor, opportunities):
        opportunity_fixed = [
            {
                key: (value if value != "" else None)
                for key, value in opportunity.items()
                if "opportunity_line_items" not in key
            }
            for opportunity in opportunities
        ]
        insert_query = sql.SQL(
            """
            INSERT INTO all_opportunity ({})
            VALUES ({})
            """
        ).format(
            sql.SQL(", ").join(
                map(sql.Identifier, opportunity_fixed[0].keys())
            ),
            sql.SQL(", ").join(
                map(sql.Placeholder, opportunity_fixed[0].keys())
            ),
        )

        try:
            cursor.executemany(insert_query, opportunity_fixed)
        except Exception as e:
            if self.debug_mode:
                insert_query_string = cursor.mogrify(
                    insert_query.as_string(cursor.connection),
                    opportunity_fixed,
                ).decode("utf-8")
                logging.info(insert_query_string)
            logging.error(
                f"[ERROR - _insert_opportunities_batch (cloudsql)] - {e}"
            )
            raise (e)

    def _insert_opportunity_lines_batch(self, cursor, project_lines):
        insert_query = sql.SQL(
            """
            INSERT INTO opportunity_line_item ({})
            VALUES ({})
        """
        ).format(
            sql.SQL(", ").join(map(sql.Identifier, project_lines[0].keys())),
            sql.SQL(", ").join(map(sql.Placeholder, project_lines[0].keys())),
        )

        try:
            cursor.executemany(insert_query, project_lines)
        except Exception as e:
            if self.debug_mode:
                insert_query_string = cursor.mogrify(
                    cursor.query, project_lines
                ).decode("utf-8")
                logging.info(insert_query_string)
            logging.error(
                f"[ERROR - _insert_opportunity_lines_batch (cloudsql)] - {e}"
            )
