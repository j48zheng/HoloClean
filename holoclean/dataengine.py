#!/usr/bin/env python

import sys
import logging
import sqlalchemy as sqla
import mysql.connector
from holoclean import *
from holoclean.dataset import *
from holoclean.utils.reader import Reader


class DataEngine:
    """TODO: Data Engine Class."""

    def __init__(self, holoEnv):
        """TODO.

        Parameters
        ----------
        parameter : type
           This is a parameter

        Returns
        -------
        describe : type
            Explanation
        """

        # Store holoclean environment
        self.holoEnv = holoEnv

        # Init database backend
        self.db_backend = self._start_db()
        self._db_connect()
        self.sparkSqlUrl = self._init_sparksql_url()
        self.sql_ctxt = self.holoEnv.sql_ctxt

        # Init spark dataframe store
        self.spark_dataframes = {}

    # Internal methods
    def _start_db(self):
        """TODO: Start MySQL database"""
        user = self.holoEnv.db_user
        pwd = self.holoEnv.db_pwd
        host = self.holoEnv.db_host
        dbname = self.holoEnv.db_name
        connection = "mysql+mysqldb://" + user + ":" + pwd + "@" + host + "/" + dbname
        return sqla.create_engine(connection)

    def _init_sparksql_url(self):
        """TODO: Start MySQL database"""
        user = self.holoEnv.db_user
        pwd = self.holoEnv.db_pwd
        host = self.holoEnv.db_host
        dbname = self.holoEnv.db_name
        jdbcUrl = "jdbc:mysql://" + host + "/" + dbname + "?user=" + user + "&password=" + pwd
        return jdbcUrl

    def _db_connect(self):
        """Connect to MySQL database"""
        try:
            self.db_backend.connect()
            self.holoEnv.log.info("Connection established to data database")
        except:
            self.holoEnv.log.warn("No connection to data database")

    # Getters
    def get_db_backend(self):
        """Return MySQL database"""
        return self.db_backend

    # Setters

    def _register_meta_table(self,table_name,table_schema):

	"""
        TO DO:store information for a table to the metatable
        """

    	schema=''
    	for attribute in table_schema:
    		schema=schema+","+str(attribute)
        
    	table_name_spc=self.dataset.spec_tb_name(table_name)
        self.add_meta(table_name, schema[1:])   
    	return table_name_spc

    def add_db_table(self, name_table, dataframe):

  	"""Add spark dataframe df with specific name table name_table in the data database 
	with spark session
	"""

        jdbcUrl="jdbc:mysql://" + self.holoEnv.db_host+"/"+self.holoEnv.db_name
        dbProperties = {
            "user" : self.holoEnv.db_user,
            "password" : self.holoEnv.db_pwd
		}
        
        dataframe.write.jdbc(jdbcUrl1, name_table,"overwrite", properties=dbProperties)

    def ingest_data(self, filepath):

	"""
        TO DO:load data from a file to a dataframe and store it on the db
        """
        # Spawn new reader and load data into dataframe
        fileReader = Reader(self.holoEnv.spark_session)
        df = fileReader.read(self, filepath)

        # Store dataframe to DB table
        schema = df.schema.names
        name_table = dataengine._register_meta_table('T', schema)
        dataengine.add_db_table(name_table, df)
        return

    def query(self, sqlQuery,spark_flag=0):

	"""
        TO DO:execute a query, uses the flag to decide if it will store the results on spark dataframe
        """

	if spark_flag==1:
		return self.query_spark(sqlQuery)
	else:
        	return self.db_backend.excute(sqlQuery)


    def query_spark(self, sqlQuery):

	"""
        TO DO:execute a query and create a dataframe from the results
        """

        dataframe = self.sql_ctxt.read.format('jdbc').options(url=self._init_sparksql_url(), dbtable="("+sqlQuery+") as tablename").load()
	return dataframe


# Member methods
    def _table_to_dataframe(self, table_name):

        """
        This method get table general name and return it as spark dataframe
        """
         
        table_get="Select * from "+self.dataset.table_name[self.dataset.attributes.index(table_name)]
        
	spark_flag=1
        return self.query(table_get,spark_flag)

    def _dataframe_to_table(self, table_name,dataframe):

        """
        This method get spark dataframe and a table_name and creates a table.
        """
        
	schema=spark_dataframe.schema.names
        specific_table_name=self._register_meta_table(table_general_name,schema)
        self.add_db_table(specific_table_name, spark_dataframe)



