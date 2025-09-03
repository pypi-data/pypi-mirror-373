import os
import json
import csv
import re
import logging
from unittest.mock import Mock
from sqlalchemy import text, select, func
import pandas as pd
from pytest import raises

from gitlabdata.orchestration_utils import (
    postgres_engine_factory,
    snowflake_engine_factory,
    data_science_engine_factory,
    query_executor,
    ds_query_dataframe,
    dataframe_uploader,
    snowflake_stage_load_copy_remove,
    execute_query_str,
    has_table,
)

config_dict = os.environ.copy()


class TestPostgresEngineFactory:
    """
    Tests the snowflake_engine_factory.
    """

    def setup(self):
        self.config_dict = os.environ.copy()
        self.config_dict["PG_PASSWORD"] = os.environ["GITLAB_METADATA_DB_PASS"]
        self.config_dict["PG_ADDRESS"] = os.environ["GITLAB_METADATA_DB_HOST"]
        self.config_dict["PG_DATABASE"] = os.environ["LEVEL_UP_METADATA_DB_NAME"]
        self.config_dict["PG_PORT"] = os.environ["GITLAB_METADATA_PG_PORT"]
        self.config_dict["PG_USERNAME"] = os.environ["GITLAB_METADATA_DB_USER"]

    def test_connection(self):
        """
        Tests that a connection can be made.
        """

        metadata_engine = postgres_engine_factory(self.config_dict)
        result = query_executor(metadata_engine, "SELECT version();")[0][0]
        logging.info(result)
        assert isinstance(result, str), f"Expected string but got {type(result)}"

    def test_autocommit(self):
        """
        Tests that on INSERT query, autocommit works, and row is inserted
        """

        metadata_engine = postgres_engine_factory(self.config_dict)
        table = "test_metadata.cursor_state"
        insert_query = f"""insert into {table} (endpoint, cursor_id, uploaded_at)
        values ('test_orchestration_utils', 'test', CURRENT_DATE)
        """
        select_query = f"""
        SELECT * FROM {table} WHERE uploaded_at = CURRENT_DATE;
        """

        with metadata_engine.connect() as conn:
            execute_query_str(conn, insert_query)
            result = execute_query_str(conn, select_query).fetchone()

        logging.info(f"select from Postgres metadata_table: {result}")
        assert result is not None


class TestSnowflakeEngineFactory:
    """
    Tests the snowflake_engine_factory.
    """

    config_dict = os.environ.copy()

    def test_connection(self):
        """
        Tests that a connection can be made.
        """

        engine = snowflake_engine_factory(config_dict, "SYSADMIN")
        result = query_executor(engine, "select current_version()")[0][0]
        logging.info(result)
        assert isinstance(result, str), f"Expected string but got {type(result)}"

    def test_database(self):
        """
        Tests that a connection can be made.
        """

        engine = snowflake_engine_factory(config_dict, "SYSADMIN")
        result = query_executor(engine, "select current_database()")[0][0]
        logging.info(result)
        assert result == "TESTING_DB"

    def test_schema(self):
        """
        Tests that a connection can be made.
        """

        engine = snowflake_engine_factory(config_dict, "SYSADMIN", "GITLAB")
        result = query_executor(engine, "select current_schema()")[0][0]
        logging.info(result)
        assert result == "GITLAB"


class TestExecuteQueryString:
    """Tests execute_query_str()"""

    def test_string_query(self):
        """
        Tests execute_query_str() can handle string queries
        """

        engine = snowflake_engine_factory(config_dict, "SYSADMIN", "GITLAB")
        query = "select current_version();"
        with engine.connect() as conn:
            result = execute_query_str(conn, query).fetchone()

        assert isinstance(
            result[0], str
        ), f"Expected result to be string but got {type(result[0])}"

    def test_sqlalchemy_query(self):
        """
        Tests execute_query_str() can handle sqlalchemy constructs for queries
        """
        engine = snowflake_engine_factory(config_dict, "SYSADMIN", "GITLAB")
        select_stmt = select(func.current_version())

        with engine.connect() as conn:
            result = execute_query_str(conn, select_stmt).fetchone()

        assert isinstance(
            result[0], str
        ), f"Expected result to be  string but got {type(result[0])}"


class TestQueryExecutor:
    """
    Tests the query_executor.
    """

    config_dict = os.environ.copy()

    def test_connection(self):
        """
        Tests that a connection can be made.
        """

        engine = snowflake_engine_factory(config_dict, "SYSADMIN", "GITLAB")
        query = "select current_version()"
        results = query_executor(engine, query)
        assert isinstance(
            results[0][0], str
        ), f"Expected string but got {type(results[0][0])}"

    def test_query_executor_reuses_connection(self):
        """Test that query_executor reuses provided connection"""
        # Setup
        mock_engine = Mock()
        mock_connection = Mock()
        mock_connection.execute.return_value.fetchall.return_value = [(1,)]

        # Execute
        results = query_executor(mock_engine, "SELECT 1", connection=mock_connection)

        # Assert
        mock_engine.connect.assert_not_called()
        mock_connection.close.assert_not_called()
        assert results == [(1,)]

    def test_query_executor_no_dispose(self):
        """Test that engine.dispose() isn't called when dispose_engine=False"""
        # Setup
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value = mock_connection

        # Execute
        query_executor(mock_engine, "SELECT 1", dispose_engine=False)

        # Assert
        mock_engine.dispose.assert_not_called()

    def test_query_executor_handles_error(self):
        """Test that connections are properly cleaned up even when query fails"""
        # Setup
        mock_engine = Mock()
        mock_connection = Mock()
        mock_engine.connect.return_value = mock_connection
        mock_connection.execute.side_effect = Exception("Database error")

        # Execute
        with raises(Exception):
            query_executor(mock_engine, "SELECT 1")

        # Assert
        mock_connection.close.assert_called_once()
        mock_engine.dispose.assert_called_once()


class TestDsQueryDataframe:
    """Tests ds_query_dataframe()"""

    config_dict = os.environ.copy()

    def test_connection(self):
        """
        Tests that a connection can be made.
        """

        conn = data_science_engine_factory(
            config_dict, "DATA_SCIENCE_LOADER", run_target="not local"
        )
        query = "select current_version()"
        df = ds_query_dataframe(conn, query)
        assert isinstance(df, pd.DataFrame), "Result is not a pandas DataFrame"
        assert len(df) == 1, f"Expected 1 row, got {len(df)} rows"
        assert len(df.columns) == 1, f"Expected 1 column, got {len(df.columns)} columns"


class TestDataFrameUploader:
    """
    Tests the dataframe_uploader.
    """

    config_dict = os.environ.copy()

    def test_upload(self):
        """
        Tests that a connection can be made.
        """

        engine = snowflake_engine_factory(config_dict, "SYSADMIN", "GITLAB")
        table = "test_table"
        dummy_dict = {"foo": [1, 2, 3], "bar": [1, 2, 3]}

        # Create a dummy DF to upload
        dummy_df = pd.DataFrame(dummy_dict)
        dataframe_uploader(dummy_df, engine, table)

        query = f"select * from {table}"
        results = query_executor(engine, query)
        query_executor(engine, f"drop table {table}")
        assert results[0][:2] == (1, 1)


class TestHasTable:
    """Tests has_table()"""

    def test_has_table(self):
        engine = snowflake_engine_factory(config_dict, "SYSADMIN")
        schema = "public"
        table = "test_has_table"

        # assert table does NOT exists after drop_query
        drop_query = f"drop table if exists {schema}.{table};"
        query_executor(engine, drop_query)

        result = has_table(engine, table, schema)
        assert result is False

        create_query = f"""create table {schema}.{table} if not exists (
            id int
        );
        """
        results = query_executor(engine, create_query)[0]
        logging.info(f"create_query results: {results}")

        # assert table exists after create_query
        result = has_table(engine, table, schema)
        assert result is True

        # cleanup
        query_executor(engine, drop_query)


class TestSnowflakeStageLoadCopyRemove:
    """
    Test snowflake_stage_load_copy_remove()

    Setup/teardown functions are seperated from test function
    so that future tests will use them automatically.
    """

    # get a copy of the environment variables
    env_vars = os.environ.copy()

    @staticmethod
    def dump_json(dict_to_dump, filename):
        """
        Dump a dictionary to a JSON file.

        Args:
            dict_to_dump (dict): The dictionary to dump to the file.
            filename (str): The name of the file to create or overwrite.
        """
        with open(filename, "w+", encoding="utf-8") as json_file:
            json.dump(dict_to_dump, json_file)

    def setup_method(self):
        """
        Set up the necessary components for testing.
        """
        # create a Snowflake engine and connection
        self.engine = snowflake_engine_factory(self.env_vars, "SYSADMIN", "GITLAB")
        self.connection = self.engine.connect()

        # create a second engine just for snowflake_stage_load_copy_remove
        self.upload_engine = snowflake_engine_factory(
            self.env_vars, "SYSADMIN", "GITLAB"
        )

        # create stage for testing
        self.test_stage = "test_utils_json_stage"
        query_executor(
            self.engine,
            f"CREATE OR REPLACE STAGE {self.test_stage} FILE_FORMAT = (TYPE = 'JSON');",
        )
        self.test_table_name = "snowflake_stage_load_copy_remove_test_table"

    def teardown_method(self):
        """
        Remove the temporary components used for testing.
        """
        # drop the test stage and table, and dispose of the connection and engine
        query_executor(
            self.engine, f"DROP STAGE IF EXISTS {self.test_stage}", dispose_engine=False
        )
        query_executor(self.engine, f"DROP TABLE IF EXISTS {self.test_table_name}")

    def test_snowflake_stage_load_copy_remove_json(self):
        """
        Test the file upload functionality.
        Two conditions to be tested:
            1. upload_dict is uploaded sucessfully and deleted from stage
            2. keep.json is placed in internal stage but not uploaded nor deleted
        """

        # create table to upload to
        create_table_query = f"""
        CREATE OR REPLACE TABLE {self.test_table_name} (
          jsontext variant,
          uploaded_at timestamp_ntz(9) DEFAULT CAST(CURRENT_TIMESTAMP() AS TIMESTAMP_NTZ(9))
        );
        """
        query_executor(self.engine, create_table_query, dispose_engine=False)

        # Create a local 'keep' file, upload it to the internal stage
        keep_file_name = "keep_in_stage_do_not_upload.json"
        self.dump_json({"1": "keep_in_stage"}, keep_file_name)
        put_query = (
            f"PUT 'file://{keep_file_name}' @{self.test_stage} AUTO_COMPRESS=TRUE;"
        )
        query_executor(self.engine, put_query, dispose_engine=False)

        # Create a local 'upload' file that will be uploaded to a table and then removed from stage
        upload_file_name = "upload.json"
        upload_dict = {"1": "uploaded"}
        self.dump_json(upload_dict, upload_file_name)

        # the upload function we are testing
        snowflake_stage_load_copy_remove(
            upload_file_name, self.test_stage, self.test_table_name, self.upload_engine
        )

        # Condition 1: Correct file was uploaded to table
        conn = self.engine.connect()
        select_query = text(f"SELECT * FROM {self.test_table_name};")
        df_select = pd.read_sql(select_query, conn)
        logging.info(f"\ndf_select: {df_select}")

        # assert that the table only has one record
        assert df_select.shape == (1, 2)

        # assert that the dictionary we uploaded is the same dictionary in the table
        json_str = df_select.iloc[0]["jsontext"]  # to_sql converted col to lower
        res_dict = json.loads(json_str)
        logging.info(f"\nres_dict: {res_dict}")
        assert res_dict == upload_dict

        # Condition 2: the interal stage should still have 'keep.json'
        stage_query = text(f"LIST @{self.test_stage};")
        df_stages = pd.read_sql(stage_query, conn)

        assert df_stages.shape[0] == 1  # should be 1 file in stage
        logging.info(f"\ndf_stages: {df_stages}")

        assert (
            f"{self.test_stage}/{keep_file_name}.gz" == df_stages["name"][0]
        )  # And the remaining file is the 'keep' file

        # remove local files
        os.remove(upload_file_name)
        os.remove(keep_file_name)
        conn.close()

    def test_snowflake_stage_load_copy_remove_csv(self):
        """
        Ensure that csv upload works
        """
        # create table to upload to
        create_table_query = f"""
        CREATE OR REPLACE TABLE {self.test_table_name} (
          first_name varchar,
          last_name varchar,
          age int
        );
        """
        query_executor(self.engine, create_table_query, dispose_engine=False)

        upload_file_name = "upload.csv"
        csv_data = [["John", "Doe", "35"], ["Jane", "Smith", "27"]]

        # Open the CSV file and write the data
        with open(upload_file_name, mode="w+", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(csv_data)

        snowflake_stage_load_copy_remove(
            upload_file_name,
            self.test_stage,
            self.test_table_name,
            self.upload_engine,
            type="csv",
        )

        # Condition 1: Correct file was uploaded to table
        select_query = text(
            f"SELECT * FROM {self.test_table_name} WHERE first_name = 'John' OR first_name = 'Jane';"
        )
        conn = self.engine.connect()
        df_select = pd.read_sql(select_query, conn)
        logging.info(f"\ndf_select: {df_select}")

        # assert that the table returns 2 records
        assert df_select.shape == (2, 3)

        # Condition 2: the interal stage should be empty now
        stage_query = text(f"LIST @{self.test_stage};")
        df_stages = pd.read_sql(stage_query, conn)
        assert df_stages.shape[0] == 0

        os.remove(upload_file_name)
        conn.close()

    def test_snowflake_stage_load_copy_remove_col_names(self):
        """
        Ensure that col_names arg works in the following scenarios:

            1. col_names argument works correctly for csv file
            2. col_names fails if arg doesn't contain parenthesis
        """
        # create table to upload to
        create_table_query = f"""
        CREATE OR REPLACE TABLE {self.test_table_name} (
          first_name varchar,
          last_name varchar,
          age int
        );
        """
        query_executor(self.engine, create_table_query, dispose_engine=False)

        upload_file_name = "upload.csv"
        csv_data = [["John", "Doe", "35"], ["Jane", "Smith", "27"]]

        # Open the CSV file and write the data
        with open(upload_file_name, mode="w+", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(csv_data)

        # Condition 1: Upload works fine with specified columns
        snowflake_stage_load_copy_remove(
            upload_file_name,
            self.test_stage,
            self.test_table_name,
            self.upload_engine,
            type="csv",
            col_names="(first_name, last_name, age)",
        )

        select_query = text(
            f"SELECT * FROM {self.test_table_name} WHERE first_name = 'John' OR first_name = 'Jane';"
        )
        conn = self.engine.connect()
        df_select = pd.read_sql(select_query, conn)
        conn.close()

        # assert that the table returns 2 records
        assert df_select.shape == (2, 3)

        # Condition 2: Fails if col_names doens't include '()'
        with raises(
            ValueError,
            match=re.escape(
                "col_names arg needs to include '(' and ')' characters, i.e `(first_name, last_name)`."
            ),
        ):
            snowflake_stage_load_copy_remove(
                upload_file_name,
                self.test_stage,
                self.test_table_name,
                self.upload_engine,
                type="csv",
                col_names="first_name, last_name, age",
            )
