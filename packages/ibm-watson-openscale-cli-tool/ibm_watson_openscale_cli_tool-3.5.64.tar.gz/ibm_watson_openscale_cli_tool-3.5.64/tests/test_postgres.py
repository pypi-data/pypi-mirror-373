import json
import responses
import argparse
import unittest
from ibm_ai_openscale_cli.database_classes.postgres import Postgres
from unittest.mock import patch, Mock, MagicMock

import psycopg2
from psycopg2 import sql
from unittest import mock
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict


SELECT_TABLES_TO_DROP = u"SELECT table_name FROM information_schema.tables WHERE table_schema = '{}' and table_type = 'BASE TABLE'"
SELECT_MEASUREMENTFACTS_SUBCOUNTS = u'SELECT "measurement", COUNT(*) AS NUM FROM "{}"."MeasurementFacts" GROUP BY "measurement" ORDER BY "measurement"'
COUNT_TABLE_ROWS = u'SELECT COUNT(*) FROM "{}"."{}"'

SELECT_TABLES_TO_DROP_SQL = u"SELECT table_name FROM information_schema.tables WHERE table_schema = 'sample_schema' and table_type = 'BASE TABLE'"
SELECT_MEASUREMENTFACTS_SUBCOUNTS_SQL = u'SELECT "measurement", COUNT(*) AS NUM FROM "sample_schema"."MeasurementFacts" GROUP BY "measurement" ORDER BY "measurement"'
COUNT_TABLE_ROWS_SQL = u'SELECT COUNT(*) FROM "sample_schema"."MeasurementFacts"'


def Identifier(param):
    return param

class SQLClass():
    def __init__(self, string):
        self._string = string
    
    def format(self, *args):
        if self._string == SELECT_TABLES_TO_DROP:
            return SELECT_TABLES_TO_DROP_SQL
        elif self._string == SELECT_MEASUREMENTFACTS_SUBCOUNTS:
            return SELECT_MEASUREMENTFACTS_SUBCOUNTS_SQL
        else:
            return COUNT_TABLE_ROWS_SQL

class tt:

    def __init__(self):
        self._sql_query = None

    def execute(self, query):
    
        self._sql_query = query
    
    def fetchall(self):
        if self._sql_query == SELECT_TABLES_TO_DROP_SQL:
            return ['MeasurementFacts']
        elif self._sql_query == SELECT_MEASUREMENTFACTS_SUBCOUNTS_SQL:
            return {[1,1], [2,1], [3,1], [4,1], [5,1]}
        else :
            return ['5']

class conn:
    class cursor:
        def __enter__(self):
            return tt()
            
        sql_query = ""
        
        def __exit__(self, statement, *params, return_rows=False):
            return
    
    def __enter__(self):
        return
        
    def __exit__(self, statement, *params, return_rows=False):
        return 

def connection(dsn=None, connection_factory=None, cursor_factory=None, **kwargs):
    return conn()
    

class TestPostgres(unittest.TestCase):
    def setUp(self):
        postgres_credentials = {"user": "admin", "password": "password", "hostname": "ibmhost", #pragma: allowlist secret 
                "port": 50000, "dbname": "sampledb"} #pragma: allowlist secret
        self.user = postgres_credentials["user"]
        self.postgres_password = postgres_credentials["password"]
        self.hostname = postgres_credentials["hostname"]
        self.port = postgres_credentials["port"]
        self.dbname = postgres_credentials["dbname"]

    @patch('psycopg2.sql.SQL', SQLClass)
    @mock.patch('psycopg2.connect', side_effect=connection)
    def test_cursor_execute(self, connection):
        
        pg = Postgres(user=self.user, password=self.postgres_password, hostname=self.hostname, port = self.port, dbname = self.dbname)
        
        response = pg._cursor_execute(SELECT_TABLES_TO_DROP, 'sample_schema' , return_rows = True)
        assert response == ['MeasurementFacts']


    @patch('psycopg2.sql.SQL', SQLClass)
    @mock.patch('psycopg2.connect', side_effect=connection)
    def test_execute(self, connection):
        
        pg = Postgres(user=self.user, password=self.postgres_password, hostname=self.hostname, port = self.port, dbname = self.dbname)
        
        response = pg._execute(SELECT_TABLES_TO_DROP, 'sample_schema' , return_rows = True)
        assert response == ['MeasurementFacts']


    @patch('psycopg2.sql.SQL', SQLClass)
    @mock.patch('psycopg2.connect', side_effect=connection)
    def test_count_datamart_rows(self, connection):
        
        pg = Postgres(user=self.user, password=self.postgres_password, hostname=self.hostname, port = self.port, dbname = self.dbname)
        
        response = pg.count_datamart_rows( 'sample_schema' , context = None)
        assert response == [['M', 5]]
        
    

        
