import unittest

from unittest.mock import patch
from ibm_ai_openscale_cli.database_classes.db2 import DB2, validate_db2_credentials
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict

db2_credentials = {"hostname": "foo.fyre.ibm.com", "username": "uname", #pragma: allowlist secret
                    "port" : "50000", #pragma: allowlist secret
                    "db": "SAMPLE",  "password": "C0wTiger", "db_type": "db2"} #pragma: allowlist secret
SELECT_TABLES_TO_DROP_SQL = u"SELECT table_name FROM information_schema.tables WHERE table_schema = 'sample_schema' and table_type = 'BASE TABLE'"
SELECT_MEASUREMENTFACTS_SUBCOUNTS_SQL = u'SELECT "measurement", COUNT(*) AS NUM FROM ""sample_schema""."MeasurementFacts" GROUP BY "measurement" ORDER BY "measurement"'
COUNT_TABLE_ROWS_SQL = u'SELECT COUNT(*) AS ROWS FROM "sample_schema"."MeasurementFacts"'

class ibm_db_mock:

    SELECT_TABLES = 0
    SELECT_MEASUREMENTFACTS = 0
    COUNT_ROWS = 0

    def __init__(self):
        self.SELECT_TABLES = 0
        self.SELECT_MEASUREMENTFACTS = 0
        self.COUNT_ROWS = 0

    @classmethod
    def connect(dsn, user='', password='', host='', database='', conn_options=None):
        return db2_credentials

    def tables(self, connection=None, param=None, schema_name=None):
        return SELECT_TABLES_TO_DROP_SQL



    @classmethod
    def fetch_assoc(self, command):

        tables = {}
        tables["TABLE_NAME"] = "MeasurementFactsss"
        if command == SELECT_TABLES_TO_DROP_SQL and self.SELECT_TABLES == 0:
            self.SELECT_TABLES = 1
            return {'TABLE_NAME' : 'MeasurementFacts'}

        elif command == SELECT_MEASUREMENTFACTS_SUBCOUNTS_SQL and self.SELECT_MEASUREMENTFACTS == 0:
            self.SELECT_MEASUREMENTFACTS = 1

            return {'measurement' : 1, 'NUM' : 1}

        elif command == COUNT_TABLE_ROWS_SQL  and self.COUNT_ROWS == 0:
            self.COUNT_ROWS = 1
            return {'ROWS' : '2' } 

    @classmethod
    def exec_immediate(self, connection, statement_str):
        return statement_str

class TestDb2(unittest.TestCase):
    def test_validate_db2_credentials(self):

        response = validate_db2_credentials(db2_credentials)
        assert response == db2_credentials


    @patch('ibm_db.connect', ibm_db_mock.connect)
    def test_process_schema_name(self):

        db2 = DB2(db2_credentials)
        response = db2._process_schema_name(schema_name = '"sample_schema"')
        assert response == '"sample_schema"'


    @patch('ibm_db.connect', ibm_db_mock.connect)
    @patch('ibm_db.tables', ibm_db_mock.tables)
    @patch('ibm_db.exec_immediate', ibm_db_mock.exec_immediate)
    @patch('ibm_db.fetch_assoc', ibm_db_mock.fetch_assoc)
    def test_count_datamart_rows(self):

        ibm_obj = ibm_db_mock()
        db2 = DB2(db2_credentials)

        response = db2.count_datamart_rows(schema_name='sample_schema')

        assert response == [['MeasurementFacts', 2], ['> 1', 1]] 