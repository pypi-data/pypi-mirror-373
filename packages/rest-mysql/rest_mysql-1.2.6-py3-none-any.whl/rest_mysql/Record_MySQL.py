# coding=utf8
"""Record SQL Module

Extends Record module to add support for SQL tables
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2020-02-12"

# Ouroboros imports
import config
from define import Parent
from tools import clone, evaluate
import jsonb

# Python imports
from decimal import Decimal
from enum import IntEnum
from functools import partial
import re
import sys
from time import sleep
from typing import List, Literal as PyLiteral

# Pip imports
import arrow
from dbutils.pooled_db import PooledDB
import json_fix
import pymysql
from pymysql.converters import escape_string

# Module imports
from . import Record_Base

# List of charsets by host
__mdCharsets = {}

# List of available connection
__mdPools = {}

# defines
MAX_RETRIES = 3

# Backwards compatibility and simplicity
DuplicateException = Record_Base.DuplicateException
RevisionException = Record_Base.RevisionException

# Duplicate record regex
DUP_ENTRY_REGEX = re.compile('Duplicate entry \'(.*?)\' for key \'(.*?)\'')

# Point regex
POINT_REGEX = re.compile('POINT\\((\-?\\d+(?:.\\d+)?) (\-?\\d+(?:.\\d+)?)\\)')

## ESelect
class ESelect(IntEnum):
	ALL			= 1
	CELL		= 2
	COLUMN		= 3
	HASH		= 4
	HASH_ROWS	= 5
	ROW			= 6

class Literal(object):
	"""Literal

	Used as a value that won't be escaped or parsed
	"""

	def __init__(self, text):
		if not isinstance(text, str):
			raise ValueError('first argument to Literal must be a string')
		self._text = text
	def __json__(self):
		return self._text
	def __str__(self):
		return self._text
	def get(self):
		return self._text

def _clear_connection(host: str):
	"""Clear Connection

	Handles removing a connection from the module list

	Args:
		host (str): The host to clear
	"""

	# If we have the connection
	if host in __mdPools:

		# Try to close the connection
		try:
			__mdPools[host].close()

			# Sleep for a second
			sleep(1)

		# Catch any exception
		except Exception as e:
			print('\n----------------------------------------')
			print('Unknown exception in Record_MySQL.Commands.__clear')
			print('host = ' + str(host))
			print('exception = ' + str(e.__class__.__name__))
			print('args = ' + ', '.join([str(s) for s in e.args]))

		# Delete the connection
		del __mdPools[host]

def _connect(conf, errcnt: int = 0):
	"""Connect

	Used to generate the individual connections in the pool

	Arguments:
		conf (dict): The configuration for the connection
		errcnt (uint): The current error count

	Returns:
		Connection
	"""

	# Create a new connection
	try:
		oCon = pymysql.connect(**conf)

	# Check for errors
	except pymysql.err.OperationalError as e:

		# Increment the error count
		errcnt += 1

		# If we've hit our max errors, raise an exception
		if errcnt == MAX_RETRIES:
			raise ConnectionError(*e.args)

		# Else just sleep for a second and try again
		else:
			sleep(1)
			return _connect(conf, errcnt)

	# Change conversions
	conv = oCon.decoders.copy()
	for k in conv:
		if k in [10,11,12]: conv[k] = str
	oCon.decoders = conv

	# Return the connection
	return oCon

def _connection(host: str) -> pymysql.Connection:
	"""Connection

	Returns a connection to the given host

	Args:
		host (str): The name of the host to connect to


	Raises:
		ConnectionError
		ValueError

	Returns:
		Connection
	"""

	# If we already have the connection, return it
	if host in __mdPools:
		return __mdPools[host].connection()

	# Look for it in config
	dConf = config.mysql.hosts[host]({
		'host': 'localhost',
		'port': 3306,
		'charset': 'utf8mb4',
		'maxconnections': 1
	})

	# Pop off max connections
	iMaxConnections = dConf.pop('maxconnections')

	oPool = PooledDB(
		creator = partial(_connect, dConf),
		maxconnections = iMaxConnections
	)

	# Store the charset
	__mdCharsets[host] = dConf['charset']

	# Store the pool and return a connection from it
	__mdPools[host] = oPool
	return oPool.connection()

def _cursor(host: str, dict_cur: bool = False) -> list:
	"""Cursor

	Returns the connection and the cursor for the given host

	Arguments:
		host (str): The name of the host
		dict_cur (bool): If true, cursor will use dicts

	Returns:
		[ Connection, Cursor ]
	"""

	# Get a connection to the host
	oCon = _connection(host)

	# Try to get a cursor on the connection
	try:

		# Start the transaction
		oCon.begin()

		if dict_cur:
			oCursor = oCon.cursor(pymysql.cursors.DictCursor)
		else:
			oCursor = oCon.cursor()

		# Make sure we're on the requested charset
		oCursor.execute('SET NAMES %s' % __mdCharsets[host])

	# If there's any exception whatsoever
	except:

		# Clear the connection and try again
		_clear_connection(host)
		return _cursor(host, dict_cur)

	# Return the connection and cursor
	return [ oCon, oCursor ]

def _print_sql(type: str, host: str, sql: str):
	"""Print SQL

	Print out a message with host and SQL information. Useful for debugging \
	problems

	Arguments:
		type (str): The type of statment
		host (str): The host the statement will be run on
		sql (str): The SQL to print
	"""
	print('----------------------------------------\n%s - %s - %s\n\n%s\n' % (
		host,
		type,
		arrow.get().format('YYYY-MM-DD HH:mm:ss'),
		sql
	))

class _wcursor(object):
	"""_wcursor

	Used with the special Python `with` method to create a connection that \
	will always be closed regardless of exceptions
	"""

	def __init__(self, host: str, dict_cur: bool = False):
		self.con, self.cursor = _cursor(host, dict_cur)

	def __enter__(self):
		return self.cursor

	def __exit__(self, exc_type, exc_value, traceback):

		# Rollback on failure
		if exc_type:
			self.con.rollback()

		# Commit on successful exit
		else:
			self.con.commit()

		# Close the cursor and connection (because it returns it to the pool)
		self.cursor.close()
		self.con.close()

def add_host(name: str, info: dict, update: bool = False):
	"""Add Host

	DEPRECATED. No longer does anything and is not needed. Host connections are
	now created as required and the details are pulled directly from config.

	Arguments:
		name (str): The name that will be used to fetch the host credentials
		info (dict): The necessary credentials to connect to the host
		update (bool): Optional, only set to True to overwrite existing info

	Returns:
		bool
	"""
	print(
		'rest_mysql.Record_MySQL.add_host is DEPRECATED and should no longer ' \
		'be used.\nEventually this warning will become an error.'
	)

def db_create(
	name: str,
	host: str = 'primary',
	charset: str | None = None,
	collate: str | None = None
) -> bool:
	"""DB Create

	Creates a DB on the given host

	Arguments:
		name (str): The name of the DB to create
		host (str): The name of the host the DB will be on
		charset (str): Optional default charset
		collate (str): Optional default collate, charset must be set to use

	Returns:
		bool
	"""

	# Generate the statement
	sSQL = 'CREATE DATABASE IF NOT EXISTS `%s%s`' % (
		Record_Base.db_prepend(), name
	)
	if charset:
		sSQL += ' DEFAULT CHARACTER SET %s' % charset
		if collate:
			sSQL += ' COLLATE %s' % collate

	# Create the DB
	return Commands.execute(host, sSQL) and True or False

def db_drop(name: str, host: str = 'primary') -> bool:
	"""DB Drop

	Drops a DB on the given host

	Arguments:
		name (str): The name of the DB to delete
		host (str): The name of the host the DB is on

	Returns:
		bool
	"""

	# Delete the DB
	return Commands.execute(host, "DROP DATABASE IF EXISTS `%s%s`" % (
		Record_Base.db_prepend(), name
	)) and True or False

def db_prepend(pre: str | None = None) -> str | None:
	"""DB Prepend

	Gets or sets the global prefix for all DBs, useful for testing/development

	Arguments:
		pre (str): The prefix to store

	Returns:
		str|None
	"""
	return Record_Base.db_prepend(pre)

def verbose(set_: bool = None) -> bool | None:
	"""Verbose

	Sets/Gets the debug flag

	Arguments:
		set_ (bool|None): Ignore to get the current value

	Returns
		bool|None
	"""
	if set_ is None: return Commands._verbose
	else: Commands._verbose = set_

# Commands class
class Commands(object):
	"""Commands class

	Used to directly interface with MySQL
	"""

	# Output SQL for debugging?
	_verbose: bool = False

	@classmethod
	def execute(cls, host: str, sql: str | List[str], errcnt: int = 0) -> int:
		"""Execute

		Used to run SQL that doesn't return any rows. Can be sent a single \
		SQL statement (str), or multiple SQL statements run as a single commit

		Args:
			host (str): The name of the connection to execute on
			sql (str|str[]): The SQL statement(s) to run
			errcnt (unsigned int): DO NOT SET, used internally

		Raises:
			ConnectionError
			DuplicateException
			ValueError

		Returns:
			unsigned int
		"""

		# Print debug if requested
		if cls._verbose: _print_sql('EXECUTE', host, sql)

		# Catch exceptions
		try:

			# Fetch a cursor
			with _wcursor(host) as oCursor:

				# If we got a str
				if isinstance(sql, str):
					s = sql
					return oCursor.execute(sql)

				# Init return
				iRet = 0

				# Go through each statement and execute it
				for s in sql:
					iRet += oCursor.execute(s)

				# Return the changed rows
				return iRet

		# If the SQL is bad
		except (pymysql.err.ProgrammingError, pymysql.err.InternalError) as e:

			# Raise an SQL Exception
			raise ValueError(
				e.args[0],
				'SQL error (%s): %s\n%s' % (
					str(e.args[0]),
					str(e.args[1]),
					str(s)
				)
			)

		# Else, a duplicate key error
		except pymysql.err.IntegrityError as e:

			# Pull out the value and the index name
			oMatch = DUP_ENTRY_REGEX.match(e.args[1])

			# If we got a match
			if oMatch:

				# Raise a Duplicate Record Exception
				raise DuplicateException(
					oMatch.group(1),
					oMatch.group(2)
				)

			# Else, raise an unkown duplicate
			raise DuplicateException(e.args[0], e.args[1])

		# Else there's an operational problem so close the connection and
		#	restart
		except pymysql.err.OperationalError as e:
			print('----------------------------------------')
			print('OPERATIONAL ERROR')
			print(e.args)
			print('')

			# If the error code is one that won't change
			if e.args[0] in [1051, 1054, 1136, 1359]:
				raise ValueError(
					e.args[0],
					'SQL error (%s): %s\n%s' % (
						str(e.args[0]),
						str(e.args[1]),
						str(s)
					)
				)

			# Increment the error count
			errcnt += 1

			# If we've hit our max errors, raise an exception
			if errcnt == MAX_RETRIES:
				raise ConnectionError(*e.args)

			# Clear the connection and try again
			_clear_connection(host)
			return cls.execute(host, sql, errcnt)

		# Else, catch any Exception
		except Exception as e:
			print('\n----------------------------------------')
			print('Unknown Error in Record_MySQL.Commands.execute')
			print('host = ' + host)
			print('sql = ' + str(sql))
			print('exception = ' + str(e.__class__.__name__))
			print('args = ' + ', '.join([str(s) for s in e.args]))

			# Rethrow
			raise e

	@classmethod
	def insert(cls, host: str, sql: str, errcnt: int = 0) -> any:
		"""Insert

		Handles INSERT statements and returns the new ID. To insert records
		without auto_increment it's best to just stick to CSQL.execute()

		Args:
			host (str): The name of the connection to into on
			sql (str): The SQL statement to run
			errcnt (uint): DO NOT SET, used internally

		Raises:
			ConnectionError
			DuplicateException
			ValueError

		Returns:
			any
		"""

		# Print debug if requested
		if cls._verbose: _print_sql('INSERT', host, sql)

		# Handle exceptions
		try:

			# Fetch a cursor
			with _wcursor(host) as oCursor:

				# Execute the insert statement
				oCursor.execute(sql)

				# Get the ID
				mInsertID = oCursor.lastrowid

				# Return the last inserted ID
				return mInsertID

		# If the SQL is bad
		except pymysql.err.ProgrammingError as e:

			# Raise an SQL Exception
			raise ValueError(
				e.args[0],
				'SQL error (%s): %s\n%s' % (
					str(e.args[0]),
					str(e.args[1]),
					str(sql)
				)
			)

		# Else, a duplicate key error
		except pymysql.err.IntegrityError as e:

			# Pull out the value and the index name
			oMatch = DUP_ENTRY_REGEX.match(e.args[1])

			# If we got a match
			if oMatch:

				# Raise a Duplicate Record Exception
				raise DuplicateException(
					oMatch.group(1),
					oMatch.group(2)
				)

			# Else, raise an unkown duplicate
			raise DuplicateException(e.args[0], e.args[1])

		# Else there's an operational problem so close the connection and
		#	restart
		except pymysql.err.OperationalError as e:

			# If the error code is one that won't change
			if e.args[0] in [1054]:
				raise ValueError(
					e.args[0],
					'SQL error (%s): %s\n%s' % (
						str(e.args[0]),
						str(e.args[1]),
						str(sql)
					)
				)

			# Increment the error count
			errcnt += 1

			# If we've hit our max errors, raise an exception
			if errcnt == MAX_RETRIES:
				raise ConnectionError(*e.args)

			# Clear the connection and try again
			_clear_connection(host)
			return cls.insert(host, sql, errcnt)

		# Else, catch any Exception
		except Exception as e:
			print('\n----------------------------------------')
			print('Unknown Error in Record_MySQL.Commands.insert')
			print('host = ' + host)
			print('sql = ' + str(sql))
			print('exception = ' + str(e.__class__.__name__))
			print('args = ' + ', '.join([str(s) for s in e.args]))

			# Rethrow
			raise e

	@classmethod
	def select(cls,
		host: str,
		sql: str,
		seltype: ESelect = ESelect.ALL,
		field: str | None = None,
		errcnt: int = 0
	) -> any:
		"""Select

		Handles SELECT queries and returns the data

		Args:
			host (str): The name of the host to select from
			sql (str): The SQL statement to run
			seltype (ESelect): The format to return the data in
			field (str): Only used by HASH_ROWS since MySQLdb has no \
				ordereddict for associative rows
			errcnt (uint): DO NOT SET, used internally

		Raises
			ConnectionError
			ValueError

		Returns:
			any
		"""

		# Print debug if requested
		if cls._verbose: _print_sql('SELECT', host, sql)

		# Get a cursor
		bDictCursor = seltype in (ESelect.ALL, ESelect.HASH_ROWS, ESelect.ROW)

		# Handle exceptions
		try:

			# Fetch a cursor
			with _wcursor(host, bDictCursor) as oCursor:

				# Run the select statement
				oCursor.execute(sql)

				# If we want all rows
				if seltype == ESelect.ALL:
					mData = list(oCursor.fetchall())

				# If we want the first cell 0,0
				elif seltype == ESelect.CELL:
					mData = oCursor.fetchone()
					if mData != None:
						mData = mData[0]

				# If we want a list of one field
				elif seltype == ESelect.COLUMN:
					mData = []
					mTemp = oCursor.fetchall()
					for i in mTemp:
						mData.append(i[0])

				# If we want a hash of the first field and the second
				elif seltype == ESelect.HASH:
					mData = {}
					mTemp = oCursor.fetchall()
					for n,v in mTemp:
						mData[n] = v

				# If we want a hash of the first field and the entire row
				elif seltype == ESelect.HASH_ROWS:

					# If the field arg wasn't set
					if field == None:
						raise ValueError(
							'Must specificy a field for the dictionary key ' \
							'when using HASH_ROWS'
						)

					mData = {}
					mTemp = oCursor.fetchall()

					for o in mTemp:
						# Store the entire row under the key
						mData[o[field]] = o

				# If we want just the first row
				elif seltype == ESelect.ROW:
					mData = oCursor.fetchone()

				# Return the results
				return mData

		# If the SQL is bad
		except pymysql.err.ProgrammingError as e:

			# Raise an SQL Exception
			raise ValueError(
				e.args[0],
				'SQL error (%s): %s\n%s' % (
					str(e.args[0]),
					str(e.args[1]),
					str(sql)
				)
			)

		# Else there's an operational problem so close the connection and
		#	restart
		except pymysql.err.OperationalError as e:

			# If the error code is one that won't change
			if e.args[0] in [1054]:
				raise ValueError(
					e.args[0],
					'SQL error (%s): %s\n%s' % (
						str(e.args[0]),
						str(e.args[1]),
						str(sql)
					)
				)

			# Increment the error count
			errcnt += 1

			# If we've hit our max errors, raise an exception
			if errcnt == MAX_RETRIES:
				raise ConnectionError(*e.args)

			# Clear the connection and try again
			_clear_connection(host)
			return cls.select(host, sql, seltype, field, errcnt)

		# Else, catch any Exception
		except Exception as e:
			print('\n----------------------------------------')
			print('Unknown Error in Record_MySQL.Commands.select')
			print('host = ' + host)
			print('sql = ' + str(sql))
			print('exception = ' + str(e.__class__.__name__))
			print('args = ' + ', '.join([str(s) for s in e.args]))

			# Rethrow
			raise e

class Record(Record_Base.Record):
	"""Record

	Extends the base Record class
	"""

	__nodeToSQL = {
		'any': False,
		'base64': False,
		'bool': 'tinyint(1) unsigned',
		'date': 'date',
		'datetime': 'datetime',
		'decimal': False,
		'float': 'double',
		'int': 'integer',
		'ip': 'char(15)',
		'json': 'text',
		'md5': 'char(32)',
		'price': False,
		'string': False,
		'time': 'time',
		'timestamp': 'timestamp',
		'tuuid': 'char(32)',
		'tuuid4': 'char(32)',
		'uint': 'integer unsigned',
		'uuid': 'char(36)',
		'uuid4': 'char(36)'
	}
	"""Node To SQL

	Used as default values for Define Node types to SQL data types
	"""

	@classmethod
	def _node_to_type(cls, struct: dict, node: str) -> str:
		"""Node To Type

		Converts the Node type to a valid MySQL field type

		Arguments:
			struct (dict): The struct associated with the instance
			field (str): The name of the node to get a type for

		Raises:
			TypeError
			ValueError

		Returns:
			str
		"""

		# Get the node's class
		sClass = struct['tree'][node].class_name()

		# If it's a regular node
		if sClass == 'Node':

			# Get the node's type
			sType = struct['tree'][node].type()

			# Can't use any in MySQL
			if sType == 'any':
				raise ValueError(node,
					'"any" nodes can not be used in Record_MySQL')

			# If the type is a string
			elif sType in [ 'base64', 'string' ]:

				# If we have options
				lOptions = struct['tree'][node].options()
				if not lOptions is None:

					# Create an enum
					return 'enum(%s)' % (','.join([
						cls.escape(struct, node, s)
						for s in lOptions
					]))

				# Else, need maximum
				else:

					# Get min/max values
					dMinMax = struct['tree'][node].minmax()

					# If we have don't have a maximum
					if dMinMax['maximum'] is None:
						raise ValueError(node,
							'"string" nodes must have a __maximum__ value if ' \
							'__sql__.type is not set in Record_MySQL'
						)

					# If the minimum matches the maximum
					if dMinMax['minimum'] == dMinMax['maximum']:

						# It's a char as all characters must be filled
						return 'char(%d)' % dMinMax['maximum']

					else:

						# long text
						if dMinMax['maximum'] == 4294967295:
							return 'longtext'
						elif dMinMax['maximum'] == 16777215:
							return 'mediumtext'
						elif dMinMax['maximum'] == 65535:
							return 'text'
						else:
							return 'varchar(%d)' % dMinMax['maximum']

			# Else, if the type is a decimal
			elif sType == 'decimal':

				# Decimals require __sql__.type set so that we know the exact
				#	length of the field
				raise ValueError(node,
					'"decimal" requires __sql__.type set in Record_MySQL, ' \
					'e.g. ' \
					'decimal(8,2) // 100,000.00 ' \
					'decimal(5,4) // 3.1415'
				)

			# Else, if the type is a price
			elif sType == 'price':

				# Get min/max values
				dMinMax = struct['tree'][node].minmax()

				# If we have don't have a maximum
				if dMinMax['maximum'] is None:
					raise ValueError(node,
						'"price" nodes must have a __maximum__ value if ' \
						'__sql__.type is not set in Record_MySQL'
					)

				# Split the maximum into whole and fration
				l = str(dMinMax['maximum']).split('.')

				# Generate the type from the length of the maximum + 2, for the
				#	cents
				return 'decimal(%i,2)' % (len(l[0]) + 2)

			# Else, if it's some form of uuid
			elif sType in [ 'tuuid', 'tuuid4', 'uuid', 'uuid4' ]:

				# If it has an sql section with the binary flag set as True
				dSQL = struct['tree'][node].special('sql')
				if dSQL and 'binary' in dSQL and dSQL['binary']:
					return 'binary(16)'
				else:
					return cls.__nodeToSQL[sType]

			# Else, get the default
			elif sType in cls.__nodeToSQL:
				return cls.__nodeToSQL[sType]

			# Else
			else:
				raise ValueError(node,
					'"%s" is not a known type to Record_MySQL')

		# Else, if it's an Array, Hash, or Parent
		elif sClass in [ 'Array', 'Hash', 'Options', 'Parent' ]:

			# Get the sql section
			dSQL = struct['tree'][node].special('sql')

			# If there's no data
			if dSQL:

				# If it's a parent and it's marked as a point
				if 'type' in dSQL and dSQL['type'] == 'point' \
					and sClass == 'Parent':

					# Return the point type
					return 'point'

				# If it doesn't exist, or there's no json flag
				if 'json' in dSQL or dSQL['json']:

					# Return the type as text so we can store the JSON
					return 'text'

			# Raise an error
			raise TypeError(node,
				'Record_MySQL can not process Define %s nodes without ' \
				'the json flag set, or the type set to "point"' % sClass
			)

		# Else, any other type isn't implemented
		else:
			raise TypeError(node,
				'Record_MySQL can not process Define %s nodes' % sClass
			)

	@classmethod
	def add_changes(cls, key: any, changes: dict, custom: dict = {}) -> bool:
		"""Add Changes

		Adds a record to the table's associated _changes table. Useful for \
		Record types that can't handle multiple levels and have children \
		tables that shouldn't be updated for every change in a single record

		Arguments:
			key (any): The ID of the record the change is associated with
			changes (dict): The dictionary of changes to add
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Raises
			RuntimeError
			ValueError

		Returns:
			bool
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If the table doesn't want changes
		if not dStruct['changes']:
			raise RuntimeError(
				'%s doesn\'t allow for changes' % dStruct['tree']._name
			)

		# If changes isn't a dict
		if not isinstance(changes, dict):
			raise ValueError('changes', 'must be a dict')

		# If Changes requires fields
		if isinstance(dStruct['changes'], list):

			# If any of the fields are missing
			for k in dStruct['changes']:
				if k not in changes:
					raise ValueError('"%s" missing from changes' % k)

		# If we have a complex primary key
		if dStruct['complex_primary']:
			sKeyFields = '`, `'.join(dStruct['primary'])
			sKeyValues = ', '.join([
				cls.escape(dStruct, sKey, key[i]) \
				for i, sKey in enumerate(dStruct['primary'])
			])

		# Else, we have single field primary key
		else:
			sKeyFields = dStruct['primary']
			sKeyValues = cls.escape(dStruct, dStruct['primary'], key)

		# Generate the INSERT statement
		sSQL = 'INSERT INTO `%s`.`%s_changes` (`%s`, `created`, `items`) ' \
				'VALUES(%s, CURRENT_TIMESTAMP, \'%s\')' % (
					dStruct['db'],
					dStruct['table'],
					sKeyFields,
					sKeyValues,
					jsonb.encode(changes)
				)

		# Create the changes record
		iRet = Commands.execute(dStruct['host'], sSQL)

		# Return based on the rows changed
		return iRet and True or False

	@classmethod
	def append(cls, key: any, array: str, item: any, custom: dict = {}) -> bool:
		"""Append

		Adds an item to a given array/list for a specific record

		Arguments:
			key (any): The ID of the record to append to
			array (str): The name of the field with the array
			item (any): The value to append to the array
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('append method not available in Record_MySQL')

	@classmethod
	def config(cls):
		"""Config

		Returns the configuration data associated with the record type

		Returns:
			dict
		"""
		raise NotImplementedError('Must implement the "config" method')

	@classmethod
	def contains(cls,
		key: any,
		array: str,
		item: any,
		custom: dict = {}
	) -> bool:
		"""Contains

		Checks if a specific item exist inside a given array/list

		Arguments:
			key (any): The ID of the record to check
			array (str): The name of the field with the array
			item (any): The value to check for in the array
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError(
			'contains method not available in Record_MySQL'
		)

	@classmethod
	def count(cls,
		key: str | None = None,
		filter: dict | List[dict] | None = None,
		custom: dict = { }
	) -> int:
		"""Count

		Returns the number of records associated with index or filter

		Arguments:
			key (any): The ID(s) to check
			filter (dict|dict[]): Additional filter(s)
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			unsigned int
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Init possible WHERE values
		lWhere = []

		# If there's no primary key, we want all records
		if key is None:
			pass

		# If we are using the primary key
		else:

			# If we have a complex primary
			if dStruct['complex_primary']:
				raise RuntimeError('key',
					'`key` can not be used with complex primary keys. Use ' \
					'`filter` instead'
				)

			# Append the ID check
			lWhere.append('`%s` %s' % (
				dStruct['primary'],
				cls.process_value(dStruct, dStruct['primary'], key)
			))

		# If we want to filter the data further
		if filter:

			# If we only have one
			if isinstance(filter, dict):
				lWhere.append(' AND '.join([
					'`%s` %s' % (n, cls.process_value(dStruct, n, v)) \
					for n,v in filter.items()
				]))

			# If we have multiple
			elif isinstance(filter, list):
				lWhere.append('(%s)' % ') OR ('.join(
					[ ' AND '.join([
						'`%s` %s' % (n, cls.process_value(dStruct, n, v)) \
						for n,v in d.items()
					]) for d in filter ]
				))

			# Else, invalid filter
			else:
				raise ValueError('filter', 'must be a dict or dict[]')

		# Build the statement
		sSQL = 'SELECT COUNT(*) FROM `%s`.`%s` ' \
				'%s ' % (
					dStruct['db'],
					dStruct['table'],
					lWhere and 'WHERE %s' % ' AND '.join(lWhere) or ''
				)

		# Run the request and return the count
		return Commands.select(dStruct['host'], sSQL, ESelect.CELL)

	@classmethod
	def _create(cls,
		record: dict,
		struct: dict,
		conflict: PyLiteral['error', 'ignore', 'replace'] = 'error',
		changes: dict | None | PyLiteral[False] = None
	) -> any:
		"""Create (base)

		Does the actual generation of the SQL and inserts the record into the
		DB. self.create and cls.create_now use this

		Arguments:
			record (dict): The raw data to enter into the DB
			struct (dict): The structure to use to generate the SQL
			conflict (str|list): Must be one of 'error', 'ignore', 'replace', \
				or a list of fields to update
			changes (dict): Data needed to store a change record, is \
				dependant on the 'changes' config value

		Raises:
			ValueError

		Returns:
			any
		"""

		# Make sure conflict arg is valid
		if not isinstance(conflict, ( tuple, list )) and \
			conflict not in ( 'error', 'ignore', 'replace' ):
			raise ValueError('conflict', conflict)

		# If the record requires revisions, make the first one
		if struct['revisions']:
			cls._revision_init(record, struct)

		# Create the string of all fields and values but the primary if it's
		#	auto incremented
		bAutoPrimary = False
		lTemp = [[], []]
		for f in struct['tree'].keys():

			# If it's the primary key with auto_primary on and the value isn't
			#	passed
			if f == struct['primary'] and \
				struct['auto_primary'] and \
				f not in record:

				# We need an auto generated key
				bAutoPrimary = True

				# If it's a got a command to run, add the field and set the
				#	value to the SQL command
				if 'auto_primary_call' in struct:

					# Add the field and set the value to the SQL variable
					lTemp[0].append('`%s`' % f)
					lTemp[1].append('@_AUTO_PRIMARY')

			# Else, just append the field name and value
			elif f in record:
				lTemp[0].append('`%s`' % f)
				if record[f] != None:
					lTemp[1].append(cls.escape(struct, f, record[f]))
				else:
					lTemp[1].append('NULL')

		# If we have replace for conflicts
		if conflict == 'replace':
			sUpdate = 'ON DUPLICATE KEY UPDATE %s' % ',\n'.join([
				"%s = VALUES(%s)" % (s, s)
				for s in lTemp[0]
			])

		elif isinstance(conflict, ( tuple,list )):
			sUpdate = 'ON DUPLICATE KEY UPDATE %s' % ',\n'.join([
				"%s = VALUES(%s)" % (s, s)
				for s in conflict
			])

		# Else, no update
		else:
			sUpdate = ''

		# Join the fields and values
		sFields	= ','.join(lTemp[0])
		sValues	= ','.join(lTemp[1])

		# Cleanup
		del lTemp

		# Generate the INSERT statement
		sSQL = 'INSERT %sINTO `%s`.`%s` (%s)\n' \
				' VALUES (%s)\n' \
				'%s' % (
					(conflict == 'ignore' and 'IGNORE ' or ''),
					struct['db'],
					struct['table'],
					sFields,
					sValues,
					sUpdate
				)

		# If the primary key is auto generated
		if bAutoPrimary:

			# If we have a specific command to run
			if 'auto_primary_call' in struct:

				# Set the SQL variable to the requested value and run the
				#	insert
				Commands.execute(struct['host'], [
					'SET @_AUTO_PRIMARY = %s' % struct['auto_primary_call'][0],
					sSQL
				])

				# Fetch the SQL variable
				record[struct['primary']] = Commands.select(
					struct['host'],
					'SELECT %s' % struct['auto_primary_call'][1],
					ESelect.CELL
				)

			# Else, assume auto_increment
			else:
				record[struct['primary']] = Commands.insert(
					struct['host'],
					sSQL
				)

			# Get the return from the primary key
			mRet = record[struct['primary']]

		# Else, the primary key was passed, we don't need to fetch it
		else:
			if not Commands.execute(struct['host'], sSQL):
				mRet = None
			else:
				mRet = True

		# If changes are required and the record was saved
		if changes is not False and mRet is not None and struct['changes']:

			# Create the changes record
			dChanges = {
				'old': None,
				'new': record
			}

			# If Changes requires fields
			if isinstance(struct['changes'], list):

				# If they weren't passed
				if not isinstance(changes, dict):
					raise ValueError('changes')

				# Else, add the extra fields
				for k in struct['changes']:
					dChanges[k] = changes[k]

			# If we have a complex primary key
			if struct['complex_primary']:
				sKeyFields = '`, `'.join(struct['primary'])
				sKeyValues = ', '.join([
					cls.escape(struct, sKey, record[sKey]) \
					for sKey in struct['primary']
				])

			# Else, we have single field primary key
			else:
				sKeyFields = struct['primary']
				sKeyValues = cls.escape(
					struct, struct['primary'], record[struct['primary']]
				)

			# Generate the INSERT statement
			sSQL = 'INSERT INTO `%s`.`%s_changes` (`%s`, `created`, `items`) ' \
					'VALUES(%s, CURRENT_TIMESTAMP, \'%s\')' % (
						struct['db'],
						struct['table'],
						sKeyFields,
						sKeyValues,
						escape_string(jsonb.encode(dChanges))
					)

			# Create the changes record
			Commands.execute(struct['host'], sSQL)

		# Return
		return mRet

	def create(self,
		conflict: PyLiteral['error', 'ignore', 'replace'] = 'error',
		changes: dict | None | PyLiteral[False] = None
	) -> any:
		"""Create

		Adds the record to the DB and returns the primary key

		Arguments:
			conflict (str|list): Must be one of 'error', 'ignore', 'replace', \
				or a list of fields to update
			changes (dict): Data needed to store a change record, is \
				dependant on the 'changes' config value

		Raises:
			ValueError

		Returns:
			any
		"""

		# If changes is False, set it to None
		if changes is False:
			changes = None

		# Call the base create and store the result
		mRes = self._create(self._dRecord, self._dStruct, conflict, changes)

		# Clear changed fields
		self._dChanged = {}

		# Return the result
		return mRes

	@classmethod
	def create_many(cls,
		records: List['Record'],
		conflict: PyLiteral['error', 'ignore', 'replace'] = 'error',
		custom: dict = {}
	) -> int:
		"""Create Many

		Inserts multiple records at once, returning the number of created rows

		Arguments:
			records (Record_MySQL.Record[]): A list of Record instances to insert
			conflict (str): Must be one of 'error', 'ignore', 'replace'
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Raises:
			RuntimeError
			ValueError

		Returns:
			unsigned int
		"""

		# Make sure conflict arg is valid
		if conflict not in ('error', 'ignore', 'replace'):
			raise ValueError('conflict', conflict)

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If changes are required
		if dStruct['changes']:
			raise RuntimeError(
				'Tables with \'changes\' flag can\'t be inserted using ' \
				'create_many'
			)

		# Create the list of fields
		lFields = []
		for f in dStruct['tree'].keys():

			# If it's not the primary key, or it is but it's not auto incrmented
			if f != dStruct['primary'] or \
				dStruct['auto_primary'] is not True:
				lFields.append(f)

		# If we have revisions, add the field
		if dStruct['revisions']:
			lFields.append(dStruct['rev_field'])

		# Initialise a list of records
		lRecords = []

		# Loop through the records
		for o in records:

			# If the record requires revisions
			if dStruct['revisions']:
				o._revision(True)

			# Loop through the fields
			lValues = []
			for f in lFields:

				# If it's the primary, and auto_primary is a string
				if f == dStruct['primary'] and \
					dStruct['auto_primary'] is not False:

					# If we generate the key ourselves, add it
					if isinstance(dStruct['auto_primary'], str):
						lValues.append('%s' % dStruct['auto_primary'])

				else:

					if f in o and o[f] != None:
						lValues.append(cls.escape(dStruct, f, o[f]))
					else:
						lValues.append('NULL')

			# Add the record
			lRecords.append("%s" % ','.join(lValues))

		# If we want to replace duplicate keys
		if conflict == 'replace':
			sUpdate = 'ON DUPLICATE KEY UPDATE %s' % ',\n'.join([
				"`%s` = VALUES(`%s`)" % (lFields[i], lFields[i])
				for i in range(len(lFields))
			])

		# Else, no update
		else:
			sUpdate = ''

		# Generate the INSERT statements
		sSQL = 'INSERT %sINTO `%s`.`%s` (`%s`) ' \
				'VALUES (%s) ' \
				'%s' % (
			(conflict == 'ignore' and 'IGNORE ' or ''),
			dStruct['db'],
			dStruct['table'],
			'`,`'.join(lFields),
			'),('.join(lRecords),
			sUpdate
		)

		# Run the statment
		iRes = Commands.execute(dStruct['host'], sSQL)

		# Returns rows inserted/changed
		return iRes

	@classmethod
	def create_now(cls,
		record: dict,
		conflict: PyLiteral['error', 'ignore', 'replace'] = 'error',
		changes: dict | None | PyLiteral[False] = None,
		custom: dict = {}
	) -> any:
		"""Create Now

		Creates a new record without creating the instance. Useful for records
		we don't need to validate because the system is making them

		Arguments:
			record (dict): The raw record data
			conflict (str): Must be one of 'error', 'ignore', 'replace'
			changes (dict): Data needed to store a change record, is \
				dependant on the 'changes' config value, set to False to \
				bypass the creation of the changes record
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			any
		"""

		# Get the struct
		dStruct = cls.struct(custom)

		# Call the base create and return the result
		return cls._create(record, dStruct, conflict, changes)

	def delete(self, changes: dict | None = None) -> bool:
		"""Delete

		Deletes the record represented by the instance

		Arguments:
			changes (dict): Data needed to store a change record, is \
				dependant on the 'changes' config value

		Raises:
			KeyError
			ValueError

		Returns:
			bool
		"""

		# If we have a complex primary
		if self._dStruct['complex_primary']:

			# If the record lacks any of the primary key values
			if not all([
				s in self._dRecord for s in self._dStruct['primary']
			]):
				raise KeyError(*self._dStruct['primary'])

			# Set the where clause
			sWhere = ' AND '.join([
				'`%s` = %s' % ( s, self.escape(
					self._dStruct, s, self._dRecord[s]
				) ) for s in self._dStruct['primary']
			])

		# Else, if we have a single field primary key
		else:

			# If the record lacks a primary key (never been created/inserted)
			if self._dStruct['primary'] not in self._dRecord:
				raise KeyError(self._dStruct['primary'])

			# Set the where clause
			sWhere = '`%s` = %s' % (
				self._dStruct['primary'],
				self.escape(
					self._dStruct,
					self._dStruct['primary'],
					self._dRecord[self._dStruct['primary']]
				)
			)

		# Generate the DELETE statement
		sSQL = 'DELETE FROM `%s`.`%s` WHERE %s' % (
			self._dStruct['db'],
			self._dStruct['table'],
			sWhere
		)

		# Delete the record
		iRet = Commands.execute(self._dStruct['host'], sSQL)

		# If no record was deleted
		if iRet != 1:
			return False

		# If changes are required
		if self._dStruct['changes']:

			# Create the changes record
			dChanges = {
				'old': self._dRecord,
				'new': None
			}

			# If Changes requires fields
			if isinstance(self._dStruct['changes'], list):

				# If they weren't passed
				if not isinstance(changes, dict):
					raise ValueError('changes')

				# Else, add the extra fields
				for k in self._dStruct['changes']:
					dChanges[k] = changes[k]

			# If we have a complex primary key
			if self._dStruct['complex_primary']:
				sKeyFields = '`, `'.join(self._dStruct['primary'])
				sKeyValues = ', '.join([
					self.escape(self._dStruct, sKey, self._dRecord[sKey]) \
					for sKey in self._dStruct['primary']
				])

			# Else, we have single field primary key
			else:
				sKeyFields = self._dStruct['primary']
				sKeyValues = self.escape(
					self._dStruct,
					self._dStruct['primary'],
					self._dRecord[self._dStruct['primary']]
				)

			# Generate the INSERT statement
			sSQL = 'INSERT INTO `%s`.`%s_changes` (`%s`, `created`, `items`) ' \
					'VALUES(%s, CURRENT_TIMESTAMP, \'%s\')' % (
						self._dStruct['db'],
						self._dStruct['table'],
						sKeyFields,
						sKeyValues,
						escape_string(jsonb.encode(dChanges))
					)

			# Insert the changes
			Commands.execute(self._dStruct['host'], sSQL)

		# Remove the primary key value(s) so we can't delete again or save
		if self._dStruct['complex_primary']:
			for s in self._dStruct['primary']:
				del self._dRecord[s]
		else:
			del self._dRecord[self._dStruct['primary']]

		# Return OK
		return True

	@classmethod
	def delete_get(cls,
		key: any | List[any] = None,
		index: str | None = None,
		filter: dict | None = None,
		custom: dict = {}
	) -> int:
		"""Delete Get

		Deletes one or many records by primary key or index and returns how \
		many were found/deleted

		Arguments:
			key (any|any[]): The primary key(s) to delete or None for all \
				records
			index (str): Not allowed, do not set
			filter (dict): Optional filter list to decide what records get \
				deleted
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Raises:
			RuntimeError

		Return:
			int
		"""

		# Don't allow index
		if index is not None:
			raise Exception(
				'index not a valid argument in Record_MySQL.delete_get'
			)

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If changes are required
		if dStruct['changes']:
			raise RuntimeError(
				'Tables with \'changes\' flag can\'t be deleted using ' \
				'delete_get'
			)

		# Init the where fields
		lWhere = []

		# If the primary key was passed
		if key is not None:

			# If we have a complex primary
			if dStruct['complex_primary']:
				raise RuntimeError('key',
					'`key` can not be used with complex primary keys. Use ' \
					'`filter` instead'
				)

			# Add the primary to the where clause
			lWhere.append('`%s` %s' % (
				dStruct['primary'],
				cls.process_value(dStruct, dStruct['primary'], key)
			))

		# If there's an additional filter
		if filter:

			# If we only have one
			if isinstance(filter, dict):
				lWhere.append(' AND '.join([
					'`%s` %s' % (n, cls.process_value(dStruct, n, v)) \
					for n,v in filter.items()
				]))

			# If we have multiple
			elif isinstance(filter, list):
				lWhere.append('(%s)' % ') OR ('.join(
					[ ' AND '.join([
						'`%s` %s' % (n, cls.process_value(dStruct, n, v)) \
						for n,v in d.items()
					]) for d in filter ]
				))

			# Else, invalid filter
			else:
				raise ValueError('filter', 'must be a dict or dict[]')

		# Build the delete statement
		sSQL = 'DELETE FROM `%s`.`%s` %s' % (
			dStruct['db'],
			dStruct['table'],
			lWhere and ('WHERE %s' % ' AND '.join(lWhere)) or ''
		)

		# Delete the record(s)
		return Commands.execute(dStruct['host'], sSQL)

	# escape method
	@classmethod
	def escape(cls, struct: dict, node: str, value: any) -> str:
		"""Escape

		Takes a value and turns it into an acceptable string for SQL

		Args:
			struct (dict): The structure associated with the instance
			node (str): The name of the node to use to escape
			value (any): The value to escape

		Raises:
			TypeError
			ValueError

		Returns:
			str
		"""

		# If it's a literal
		if isinstance(value, Literal):
			return value.get()

		elif value is None:
			return 'NULL'

		else:

			# Get the Node's class
			sClass = struct['tree'][node].class_name()

			# If it's a standard Node
			if sClass == 'Node':

				# Get the type
				type_ = struct['tree'][node].type()

				# If we're escaping a bool
				if type_ == 'bool':

					# If it's already a bool or a valid int representation
					if isinstance(value, bool) or \
						(isinstance(value, int) and value in [0,1]):
						return (value and '1' or '0')

					# Else if it's a string
					elif isinstance(value, str):

						# If it's t, T, 1, f, F, or 0
						return (value in ('true', 'True', 'TRUE', 't', 'T', '1') \
			  				and '1' \
							or '0'
						)

				# Else if it's a date, md5, or UUID, return as is
				elif type_ in ('base64', 'date', 'datetime', 'md5', 'time'):
					return "'%s'" % value

				# Else if the value is a decimal value
				elif type_ in ('decimal', 'float', 'price'):
					return str(float(value))

				# Else if the value is an integer value
				elif type_ in ('int', 'uint'):
					return str(int(value))

				# Else if it's a timestamp
				elif type_ == 'timestamp' and \
					(isinstance(value, int) or re.match('^\d+$', value)):
					return 'FROM_UNIXTIME(%s)' % str(value)

				# Else, if it's a trimmed binary uuid, unhex it
				elif type_ in [ 'tuuid', 'tuuid4', 'uuid', 'uuid4' ]:

					# If it is in the to process dict
					if node in struct['to_process']:

						# If it's a trimmed uuid, unhex it
						if struct['to_process'][node] in [ 'tuuid', 'tuuid4' ]:
							return "UNHEX('%s')" % value

						# Else, if it's a full uuid, convert it to binary
						elif struct['to_process'][node] in [ 'uuid', 'uuid4' ]:
							return "`%s`.UUID_TO_BIN('%s')" % (
								struct['db'],  value
							)

					# Else, just throw single quotes around it
					else:
						return "'%s'" % value

				# Else it's a standard escape
				else:
					return "'%s'" % escape_string(value)

			# Else, if it's a Parent node
			elif sClass in ['Array', 'Hash', 'Options', 'Parent']:

				# If it's in the 'to_process' section
				if node in struct['to_process']:

					# If it's a point
					if struct['to_process'][node] == 'point':

						# If it's a parent
						if sClass == 'Parent':

							# Check the value
							try:
								evaluate(value, [ 'lat', 'long' ])
							except ValueError as e:
								raise ValueError(
									struct['tree'][node].name(),
									'must contain a "lat" and "long" value'
								)

							# Convert the values to Decimals to make sure
							#	they're valid
							dPoint = {}
							for s in [ 'lat', 'long' ]:
								try:
									dPoint[s] = Decimal(value[s])
								except ValueError:
									dPoint[s] = '0.0'

							# Return it as an SQL POINT
							return 'ST_GeomFromText(\'POINT(%s %s)\', 4326)' % (
								dPoint['lat'], dPoint['long']
							)

					# If it's json, encode it, then escape it at the host level
					elif struct['to_process'][node] == 'json':
						return "'%s'" % escape_string(jsonb.encode(value))

			# Else, any other type isn't implemented
			else:
				raise TypeError(
					'Record_MySQL can not process Define %s nodes' % sClass
				)

	@classmethod
	def exists(cls,
		key: any, index: str | None = None, custom: dict = {}
	) -> bool:
		"""Exists

		Returns the primary key of the record for the specified ID or \
		unique index value found, else False if no record is found. Key will \
		accept multiple values without an error, but only to tell if ANY key \
		exists, and not if all keys exist. Be warned though, for complex \
		primary keys, this will only work as expected if one value is static, \
		e.g.

		Record.exists((
			[ 'key1_0', 'key1_1', 'key1_2', 'key1_3' ],
			'key2'
		))

		Attempting to pass two or more lists to a key in the primary, will \
		raise an exception

		Arguments:
			key (any | tuple[any]): The primary key to check
			index (str): Not allowed, do not set
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""

		# Don't allow index
		if index is not None:
			raise Exception(
				'index not a valid argument in Record_MySQL.exists'
			)

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If we have no primary key
		if not dStruct['primary']:
			raise RuntimeError(
				'exists', 'record does not contain a primary key'
			)

		# If we have a complex primary key
		if dStruct['complex_primary']:

			# Get the number of lists
			if len([ True for m in key if isinstance(m, list) ]) > 1:
				raise ValueError('key',
					'Can not have multiple lists as part of `key` when ' \
					'calling exists on a complex primary key record'
				)

			# Use filter to find the record
			dRecord = cls.filter(
				{ sKey: key[i] for i, sKey in enumerate(dStruct['primary']) },
				raw = dStruct['primary'],
				limit = 1,
				custom = custom
			)
			if dRecord:
				return dRecord

		# Else, we have a single field
		else:

			# Use the get method to find the record
			dRecord = cls.get(
				key,
				raw = [ dStruct['primary'] ],
				limit = 1,
				custom = custom
			)
			if dRecord:
				return dRecord[dStruct['primary']]

		# Nothing was returned, return failure
		return False

	def field_set(self, field: str, val: any) -> 'Record':
		"""Field Set

		Overwrites Record_Base.Record.field_set to allow for setting Literals, \
		values that are not verified and then sent to the server as is

		Arguments:
			field (str): The name of the field to set
			val (any): The value to set the field to

		Raises:
			KeyError: field doesn't exist in the structure of the record
			ValueError: value is not valid for the field

		Returns:
			self for chaining
		"""

		# If the value is actually a literal, accept it as is
		if isinstance(val, Literal):

			# If we need to keep changes
			if self._dStruct['changes']:
				if self._dOldRecord is None:
					self._dOldRecord = clone(self._dRecord)

			# If we still have a dict for changes (not a total replace)
			if isinstance(self._dChanged, dict):
				self._dChanged[field] = True

			# Set the field as is
			self._dRecord[field] = val

		# Else, allow the parent to validate the value
		else:
			super().field_set(field, val)

	# filter static method
	@classmethod
	def filter(cls,
		fields: dict | List[dict],
		raw: str | List[str] | PyLiteral[True] | None = None,
		distinct: bool = False,
		orderby: str | List[str] | List[List[str]] | None = None,
		limit: int | tuple | None = None,
		custom: dict = {}
	) -> 'Record' | List['Record'] | dict | List[dict]:
		"""Filter

		Finds records based on the specific fields and values passed

		Arguments:
			fields (dict | dict[]): One or more dictionaries of field names to \
				the values they should match, dict values are AND'ed together, \
				and each of the list is OR'ed
			raw (bool|str|list): Optional, default returns a list of Records, \
				set to True to return a list of dicts, pass a list to return \
				a list of dicts with only the fields provided, or pass a \
				single string to return a list of just those values
			distinct (bool): Only return distinct data
			orderby (str|str[]): A field or fields to order the results by
			limit (int|tuple): The limit and possible starting point
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Raises:
			ValueError

		Returns:
			Record | Record[] | dict | dict[]
		"""

		# By default we will return multiple records
		bMultiRecords = True

		# Are we returning dicts/Records, or a column?
		bMultiFields = not isinstance(raw, str)

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Generate the SELECT fields
		sFields = cls.process_select(
			dStruct,
			(raw is None or raw is True) and \
				dStruct['tree'].keys() or \
				(bMultiFields and raw or [ raw ])
		)

		# Go through each value
		lWhere = []

		# If we only have one
		if isinstance(fields, dict):
			lWhere.append(' AND '.join([
				'`%s` %s' % (n, cls.process_value(dStruct, n, v)) \
				for n,v in fields.items()
			]))

		# If we have multiple
		elif isinstance(fields, list):
			lWhere.append('(%s)' % ') OR ('.join(
				[ ' AND '.join([
					'`%s` %s' % (n, cls.process_value(dStruct, n, v)) \
					for n,v in d.items()
				]) for d in fields ]
			))

		# Else, invalid fields
		else:
			raise ValueError('fields', 'must be a dict or dict[]')

		# If the order isn't set
		if orderby is None:
			sOrderBy = ''

		# Else, generate it
		else:

			# If the field is a list of fields
			if isinstance(orderby, (list, tuple)):

				# Go through each field
				lOrderBy = []
				for i in orderby:
					if isinstance(i, (list,tuple)):
						lOrderBy.append('`%s` %s' % (i[0], i[1]))
					else:
						lOrderBy.append('`%s`' % i)
				sOrderBy = 'ORDER BY %s' % ','.join(lOrderBy)

			# Else there's only one field
			else:
				sOrderBy = 'ORDER BY `%s`' % orderby

		# If the limit isn't set
		if limit is None:
			sLimit = ''

		# Else, generate it
		else:

			# If we got an int
			if isinstance(limit, int):
				sLimit = 'LIMIT %d' % limit
				if limit == 1:
					bMultiRecords = False

			# If we got a tuple/list
			elif isinstance(limit, (list,tuple)):
				sLimit = 'LIMIT %d, %d' % (limit[0], limit[1])
				if limit[1] == 1:
					bMultiRecords = False

			# Else, invalid limit format
			else:
				raise ValueError('limit', 'Invalid limit passed to filter')

		# Build the statement
		sSQL = 'SELECT %s%s FROM `%s`.`%s` ' \
				'WHERE %s ' \
				'%s %s' % (
					distinct and 'DISTINCT ' or '',
					sFields,
					dStruct['db'],
					dStruct['table'],
					' AND '.join(lWhere),
					sOrderBy,
					sLimit
				)

		# If we only want multiple records
		if bMultiRecords:

			# Get all the records
			lRecords = Commands.select(
				dStruct['host'],
				sSQL,
				bMultiFields and ESelect.ALL or ESelect.COLUMN
			)

			# If there's no data, return an empty list
			if not lRecords:
				return []

			# If we have any fields that need to be processed / decoded
			if dStruct['to_process']:
				if bMultiFields:
					for d in lRecords:
						cls.process_record(dStruct['to_process'], d)
				elif raw in dStruct['to_process']:
					for i, m in enumerate(lRecords):
						lRecords[i] = cls.process_field(
							dStruct['to_process'][raw], m
						)

			# If Raw requested, return as is
			if raw:
				return lRecords

			# Else create instances for each
			else:
				return [cls(d, custom) for d in lRecords]

		# Else, we want one record
		else:

			# Get one row or cell
			dRecord = Commands.select(
				dStruct['host'],
				sSQL,
				bMultiFields and ESelect.ROW or ESelect.CELL
			)

			# If there's no data, return None
			if not dRecord:
				return None

			# If we have any fields that need to be processed / decoded
			if dStruct['to_process']:
				if bMultiFields:
					cls.process_record(dStruct['to_process'], dRecord)
				elif raw in dStruct['to_process']:
					dRecord = cls.process_field(
						dStruct['to_process'][raw], dRecord
					)

			# If Raw requested, return as is
			if raw:
				return dRecord

			# Else create an instances
			else:
				return cls(dRecord, custom)

	@classmethod
	def generate_config(cls,
		tree: Parent,
		special: str = 'sql',
		override: dict | None = None
	) -> dict:
		"""Generate Config

		Generates record specific config based on the Define Parent passed

		Arguments:
			tree (Define.Parent): the tree associated with the record type
			special (str): The special section used to identify the child info
			override (dict): Used to override any data from the tree

		Raises:
			TypeError

		Returns:
			dict
		"""

		# Get the based config from the parent
		dConfig = super().generate_config(tree, special, override)

		# Add an empty process section
		dConfig['to_process'] = { }

		# Add an empty rename section
		dConfig['to_rename'] = { }

		# If the primary key is a list / tuple, mark it as complex
		dConfig['complex_primary'] = \
			isinstance(dConfig['primary'], ( list, tuple ))

		# If it's complex
		if dConfig['complex_primary']:

			# Make sure we have all the fields
			if not all(s in tree for s in dConfig['primary']):
				raise ValueError(
					'primary', 'not all primary key fields exist in the tree'
				)

			# If the auto_increment value is set
			if dConfig['auto_primary']:
				raise ValueError(
					'auto_primary',
					'can not be set to true for complex primary keys'
				)

		# Else, just make sure we have the primary
		else:
			if dConfig['primary'] and dConfig['primary'] not in tree:
				raise ValueError(
					'primary', 'primary key field doe not exist in the tree'
				)

		# Go through each node in the tree
		for k in tree:

			# Get the classname
			sClass = tree[k].class_name()

 			# If it's a Node
			if sClass == 'Node':

				# If it's json or bool type
				sType = tree[k].type()
				if sType == 'bool':

					# Add it to the list
					dConfig['to_process'][k] = sType

				# Else, if it's a timestamp
				elif sType == 'timestamp':

					# Add it to the rename dict
					dConfig['to_rename'][k] = 'timestamp'

				# Else, if it's a UUID
				elif sType in [ 'tuuid', 'tuuid4', 'uuid', 'uuid4' ]:

					# If it has an SQL section with a binary flag
					dSQL = tree[k].special('sql')
					if dSQL and 'binary' in dSQL and dSQL['binary']:
						bBinary = True
						dConfig['to_rename'][k] = sType
						dConfig['to_process'][k] = sType
					else:
						bBinary = False

					# If it's the primary field
					if k == dConfig['primary']:

						# If it's meant to be auto generated
						if dConfig['auto_primary']:

							# If it's binary
							if bBinary:
								dConfig['auto_primary_call'] = \
									sType in [ 'uuid', 'uuid4' ] and [
										'`%s`.UUID_TO_BIN(UUID())' % \
											dConfig['db'],
										'`%s`.BIN_TO_UUID(@_AUTO_PRIMARY)' % \
											dConfig['db']
									] or [
										"UNHEX(REPLACE(UUID(), '-', ''))",
										'LOWER(HEX(@_AUTO_PRIMARY))'
									]

							# Else, if it's a string
							else:
								dConfig['auto_primary_call'] = [
									sType in [ 'uuid', 'uuid4' ] and \
										'UUID()' or
										"REPLACE(UUID(), '-', '')",
									'@_AUTO_PRIMARY'
								]

			# Else, if it's an object/dict type
			elif sClass in [ 'Array', 'Hash', 'Options', 'Parent' ]:

				# If it has an SQL section
				dSQL = tree[k].special('sql')
				if dSQL:

					# If it's a parent and it's marked as a point
					if 'type' in dSQL and dSQL['type'] == 'point' and \
						sClass == 'Parent':

						# If we don't have the necessary fields
						if sorted(list(tree[k].keys())) != [ 'lat', 'long' ]:
							raise TypeError(k,
								'sql.point must contain only "lat" and ' \
								'"long" keys'
							)

						# If the fields are invalid
						if tree[k]['lat'].type() != 'decimal' or \
							tree[k]['long'].type() != 'decimal':
							raise TypeError(k,
								'sql.point.lat and sql.point.long type ' \
								'must be set to "decimal"'
							)

						# Add it to the process list
						dConfig['to_process'][k] = 'point'

						# Add it to the rename dict
						dConfig['to_rename'][k] = 'point'

					# Else, if it has the json flag
					elif 'json' in dSQL and dSQL['json']:

						# Add it to the list
						dConfig['to_process'][k] = 'json'

		# Return the final config
		return dConfig

	@classmethod
	def get(cls,
		key: any | List[any] | None = None,
		index: None = None,
		filter: dict | None = None,
		match: None = None,
		raw: str | List[str] | PyLiteral[True] | None = None,
		distinct: bool = False,
		orderby: str | List[str] | List[List[str]] | None = None,
		limit: int | tuple | None = None,
		custom: dict = {}
	) -> 'Record' | List['Record'] | dict | List[dict] | None:
		"""Get

		Returns records by primary key or index, can also be given an extra \
		filter

		Arguments:
			key (str|str[]): The primary key(s) to fetch from the table
			index (str): N/A in MySQL
			filter (dict): Additional filter
			match (tuple): N/A in MySQL
			raw (bool|str|list): Optional, default returns a list of Records, \
				set to True to return a list of dicts, pass a list to return \
				a list of dicts with only the fields provided, or pass a \
				single string to return a list of just those values
			distinct (bool): Only return distinct data
			orderby (str|str[]): A field or fields to order the results by
			limit (int|tuple): The limit and possible starting point
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Raises:
			TypeError

		Returns:
			Record|Record[]|dict|dict[]
		"""

		# Don't allow index or match in MySQL
		if index is not None:
			raise TypeError('index not a valid argument in Record_MySQL.get')
		if match is not None:
			raise TypeError('match not a valid argument in Record_MySQL.get')

		# By default we will return multiple records
		bMultiRecords = True

		# Are we returning dicts/Records, or a column?
		bMultiFields = not isinstance(raw, str)

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Generate the SELECT fields
		sFields = cls.process_select(
			dStruct,
			(raw is None or raw is True) and \
				dStruct['tree'].keys() or \
				(bMultiFields and raw or [ raw ])
		)

		# Init the where fields
		lWhere = []

		# If there's an id
		if key is not None:

			# If we have a complex primary key
			if dStruct['complex_primary']:
				raise RuntimeError('get',
					'can not use .get() with complex primary key records. ' \
					'Use .filter() instead.'
				)

			# Add the primary
			lWhere.append('`%s` %s' % (
				dStruct['primary'],
				cls.process_value(dStruct, dStruct['primary'], key)
			))

			# Check if the key is a single value
			if not isinstance(key, (dict,list,tuple)) or \
				isinstance(key, str):
				bMultiRecords = False

		# If there's an additional filter
		if filter:

			# If we only have one
			if isinstance(filter, dict):
				lWhere.append(' AND '.join([
					'`%s` %s' % (n, cls.process_value(dStruct, n, v)) \
					for n,v in filter.items()
				]))

			# If we have multiple
			elif isinstance(filter, list):
				lWhere.append('(%s)' % ') OR ('.join(
					[ ' AND '.join([
						'`%s` %s' % (n, cls.process_value(dStruct, n, v)) \
						for n,v in d.items()
					]) for d in filter ]
				))

			# Else, invalid filter
			else:
				raise ValueError('filter', 'must be a dict or dict[]')

		# If the order isn't set
		if orderby is None:
			sOrderBy = ''

		# Else, generate it
		else:

			# If the field is a list of fields
			if isinstance(orderby, (list, tuple)):

				# Go through each field
				lOrderBy = []
				for i in orderby:
					if isinstance(i, (list,tuple)):
						lOrderBy.append('`%s` %s' % (i[0], i[1]))
					else:
						lOrderBy.append('`%s`' % i)
				sOrderBy = 'ORDER BY %s' % ','.join(lOrderBy)

			# Else there's only one field
			else:
				sOrderBy = 'ORDER BY `%s`' % orderby

		# If the limit isn't set
		if limit is None:
			sLimit = ''

		# Else, generate it
		else:

			# If we got an int
			if isinstance(limit, int):
				sLimit = 'LIMIT %d' % limit
				if limit == 1:
					bMultiRecords = False

			# If we got a tuple/list
			elif isinstance(limit, (list,tuple)):
				sLimit = 'LIMIT %d, %d' % (limit[0], limit[1])
				if limit[1] == 1:
					bMultiRecords = False

		# Build the statement
		sSQL = 'SELECT %s%s FROM `%s`.`%s` ' \
				'%s ' \
				'%s %s' % (
					distinct and 'DISTINCT ' or '',
					sFields,
					dStruct['db'],
					dStruct['table'],
					lWhere and 'WHERE %s' % ' AND '.join(lWhere) or '',
					sOrderBy,
					sLimit
				)

		# If we only want multiple records
		if bMultiRecords:

			# Get all the records
			lRecords = Commands.select(
				dStruct['host'],
				sSQL,
				bMultiFields and ESelect.ALL or ESelect.COLUMN
			)

			# If there's no data, return an empty list
			if not lRecords:
				return []

			# If we have any fields that need to be processed / decoded
			if dStruct['to_process']:
				if bMultiFields:
					for d in lRecords:
						cls.process_record(dStruct['to_process'], d)
				elif raw in dStruct['to_process']:
					for i, m in enumerate(lRecords):
						lRecords[i] = cls.process_field(
							dStruct['to_process'][raw], m
						)

			# If Raw requested, return as is
			if raw:
				return lRecords

			# Else create instances for each
			else:
				return [cls(d, custom) for d in lRecords]

		# Else, we want one record
		else:

			# Get one row or cell
			dRecord = Commands.select(
				dStruct['host'],
				sSQL,
				bMultiFields and ESelect.ROW or ESelect.CELL
			)

			# If there's no data, return None
			if not dRecord:
				return None

			# If we have any fields that need to be processed / decoded
			if dStruct['to_process']:
				if bMultiFields:
					cls.process_record(dStruct['to_process'], dRecord)
				elif raw in dStruct['to_process']:
					dRecord = cls.process_field(
						dStruct['to_process'][raw], dRecord
					)

			# If Raw requested, return as is
			if raw:
				return dRecord

			# Else create an instances
			else:
				return cls(dRecord, custom)

	@classmethod
	def get_changes(cls,
		key: any,
		orderby: str | List[str] | List[List[str]] | None = None,
		custom: dict = {}
	) -> List[dict]:
		"""Get Changes

		Returns the changes record associated with the primary record and \
		table. Used by Record types that have the 'changes' flag set.

		Arguments:
			key (any): The of the primary record to fetch changes for
			orderby (str|str[]): A field or fields to order the results by
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			dict[]
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If the order isn't set
		if orderby is None:
			sOrderBy = ''

		# Else, generate it
		else:

			# If the field is a list of fields
			if isinstance(orderby, (list, tuple)):

				# Go through each field
				lOrderBy = []
				for i in orderby:
					if isinstance(i, (list,tuple)):
						lOrderBy.append('`%s` %s' % (i[0], i[1]))
					else:
						lOrderBy.append('`%s`' % i)
				sOrderBy = 'ORDER BY %s' % ','.join(lOrderBy)

			# Else there's only one field
			else:
				sOrderBy = 'ORDER BY `%s`' % orderby

		# Generate the SELECT statement
		sSQL = 'SELECT `%s`, `created`, `items` ' \
				'FROM `%s`.`%s_changes` ' \
				'WHERE `%s` %s ' \
				'%s' % (
			dStruct['primary'],
			dStruct['db'],
			dStruct['table'],
			dStruct['primary'],
			cls.process_value(dStruct, dStruct['primary'], key),
			sOrderBy
		)

		# Fetch all records
		lRecords = Commands.select(dStruct['host'], sSQL, ESelect.ALL)

		# Go through each record and turn the items from JSON to dicts
		for i in range(len(lRecords)):
			lRecords[i]['items'] = jsonb.decode(lRecords[i]['items'])

		# Return the records
		return lRecords

	@classmethod
	def process_field(cls, type: str, value: any) -> any:
		"""Process Field

		Decodes a JSON, bool, or other non-standard field and returns it

		Arguments:
			type (str): The type of field
			val (any): The value to process

		Returns:
			any
		"""

		# If it's a bool, convert it from 1-0 to True-False
		if type == 'bool':
			return value and True or False

		# Else, if it's a json, decode it
		elif type == 'json':
			return jsonb.decode(value)

		# Else, if it's a point
		elif type == 'point':
			oM = POINT_REGEX.match(value)
			try:
				return { 'lat': oM.group(1), 'long': oM.group(2) }
			except AttributeError:
				return { 'lat': '0.0', 'long': '0.0' }

		# Else, return as is
		else:
			return value

	@classmethod
	def process_record(cls, fields: dict, record: dict):
		"""Process Record

		Goes through a record and decodes any JSON, bool or other non-standard \
		fields in place, does NOT return a new dict

		Arguments:
			fields (dict): The dictionary of fields to their decoding type
			record (dict): The record to process
		"""

		# Go through each field
		for sField, sType in fields.items():

			# If it's in the record and it's got a value
			if sField in record and record[sField] is not None:

				# Convert it
				record[sField] = cls.process_field(sType, record[sField])

	@classmethod
	def process_select(cls,
		struct: dict,
		select: List[str],
		table: str = None
	) -> str:
		"""Process Select

		Goes through select fields and renames them based on their type so that
		we get the expected values. Returns a single string with all the fields
		passed.

		Arguments:
			struct (dict): The structure of the instance
			select (str[]): The list of select fields to convert
			table (str): Optional table to add to the fields, useful for joins

		Returns:
			str
		"""

		# Init the new list
		lRet = [ ]

		# If we have no renames
		if struct['to_rename'] == []:
			return ', '.join([ '`%s`' % f for f in select ])

		# Step through all the select fields
		for f in select:

			# If it's in the renames
			if f in struct['to_rename']:

				# If it's a point
				if struct['to_rename'][f] == 'point':
					lRet.append( table \
						and f'ST_AsText(`{table}`.`{f}`) as `{f}`' \
						or f'ST_AsText(`{f}`) as `{f}`'
					)

				# Else, if it's a timestamp
				elif struct['to_rename'][f] == 'timestamp':
					lRet.append( table \
						and f'UNIX_TIMESTAMP(`{table}`.`{f}`) as `{f}`' \
						or f'UNIX_TIMESTAMP(`{f}`) as `{f}`'
					)

				# Else, if it's a trimmed uuid
				elif struct['to_rename'][f] in [ 'tuuid', 'tuuid4' ]:
					lRet.append( table \
						and f'LOWER(HEX(`{table}`.`{f}`)) as `{f}`' \
						or f'LOWER(HEX(`{f}`)) as `{f}`'
					)

				# Else, if it's a uuid
				elif struct['to_rename'][f] in [ 'uuid', 'uuid4' ]:
					lRet.append( table \
						and f'`{struct["db"]}`.BIN_TO_UUID(`{table}`.`{f}`) as `{f}`' \
						or f'`{struct["db"]}`.BIN_TO_UUID(`{f}`) as `{f}`'
					)

			# Else, add it as is
			else:
				lRet.append(table and f'`{table}`.`{f}`' or f'`{f}`')

		# Return the new list
		return ', '.join(lRet)

	@classmethod
	def process_value(cls, struct: dict, field: str, value: any) -> str:
		"""Process Value

		Takes a field and a value or values and returns the proper SQL \
		to look up the values for the field

		Args:
			struct (dict): The structure associated with the record
			field (str): The name of the field
			value (any): The value as a single item, list, or dictionary

		Returns:
			str
		"""

		# Get the field node
		oNode = struct['tree'][field]

		# If the value is a list
		if isinstance(value, ( list, tuple )):

			# Build the list of values
			lValues = []
			for i in value:
				# If it's None
				if i is None:
					lValues.append('NULL')
				else:
					lValues.append(cls.escape(struct, field, i))
			sRet = 'IN (%s)' % ','.join(lValues)

		# Else if the value is a dictionary
		elif isinstance(value, dict):

			# If it has a start and end
			if 'between' in value:
				sRet = 'BETWEEN %s AND %s' % (
					cls.escape(struct, field, value['between'][0]),
					cls.escape(struct, field, value['between'][1])
				)

			# Else if we have a less than
			elif 'lt' in value:
				sRet = '< ' + cls.escape(struct, field, value['lt'])

			# Else if we have a greater than
			elif 'gt' in value:
				sRet = '> ' + cls.escape(struct, field, value['gt'])

			# Else if we have a less than equal
			elif 'lte' in value:
				sRet = '<= ' + cls.escape(struct, field, value['lte'])

			# Else if we have a greater than equal
			elif 'gte' in value:
				sRet = '>= ' + cls.escape(struct, field, value['gte'])

			# Else if we have a not equal
			elif 'neq' in value:

				# If the value is a list
				if isinstance(value['neq'], ( list, tuple )):

					# Build the list of values
					lValues = []
					for i in value['neq']:
						# If it's None
						if i is None:
							lValues.append('NULL')
						else:
							lValues.append(
								cls.escape(struct, field, i)
							)
					sRet = 'NOT IN (%s)' % ','.join(lValues)

				# Else, it must be a single value
				else:
					if value['neq'] is None:
						sRet = 'IS NOT NULL'
					else:
						sRet = '!= ' + cls.escape(
							struct, field, value['neq']
						)

			elif 'like' in value:
				sRet = 'LIKE ' + cls.escape(
					struct, field, value['like']
				)

			# No valid key in dictionary
			else:
				raise ValueError(
					'key must be one of "between", "lt", "gt", "lte", "gte", ' \
					'or "neq"'
				)

		# Else, it must be a single value
		else:

			# If it's None
			if value is None: sRet = 'IS NULL'
			else: sRet = '= ' + cls.escape(struct, field, value)

		# Return the processed value
		return sRet

	@classmethod
	def provide_select(cls,
		fields: List[str] = None,
		without: List[str] = None,
		table: bool = False,
		custom: dict = {}
	) -> str:
		"""Provide Select

		Uses the class instance to generate a string of fields useable for a
		SELECT statement so that custom methods don't need to worry about field
		changes when generate custom SQL.

		Arguments:
			fields (str[]): Optional list of fields to use if you only want
				some. Ignore to get all fields associated with the Record
			without (str[] | '_'): Optional list of field not to include,
				helpful to include all fields minus some to avoid needing to
				make changes if new fields are added. Set to '_' instead of a
				list to remove all fields prefixed by the underscore
			table (bool): Optional, set to true to include the table as a prefix
				for the field names. i.e. `table`.`field` instead of just
				`field`
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Raises:
			ValueError if both `fields` and `without` are set

		Returns:
			str
		"""

		# Get the struct
		dS = cls.struct(custom)

		# If fields and without is set
		if fields and without:
			raise ValueError('Can not set both fields and without')

		# Else, if fields is set
		elif fields:
			lFields = fields

		# Else, regardless if without is set, we can use keys to get all fields
		else:
			lFields = cls.keys(without)

		# Pass the info to the static method
		return cls.process_select(
			dS,
			lFields,
			table and dS['table'] or None
		)

	@classmethod
	def remove(cls,
		key: any, array: str, index: int, custom: dict = {}
	) -> bool:
		"""Remove

		Removes an item from a given array/list for a specific record

		Arguments:
			key (any): The ID of the record to remove from
			array (str): The name of the field with the array
			index (uint): The index of the array to remove
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('remove method not available in Record_MySQL')

	def save(self, replace: bool = False, changes: dict = None) -> bool:
		"""Save

		Updates the record in the DB and returns true if anything has changed, \
		or a new revision number of the record is revisionable

		Arguments:
			replace (bool): If true, replace all fields instead of updating
			changes (dict): Data needed to store a change record, is
				dependant on the 'changes' config value

		Raises:
			KeyError
			RevisionException
			ValueError

		Returns:
			bool
		"""

		# If no fields have been changed, nothing to do
		if not self._dChanged:
			return False

		# If we have a complex primary key
		if self._dStruct['complex_primary']:

			# If any of the fields are missing
			if not all(s in self._dRecord for s in self._dStruct['primary']):
				raise KeyError(self._dStruct['primary'])

			# Generate the where clause
			sWhere = ' AND '.join([
				'`%s` = %s' % (
					s, self.escape(self._dStruct, s, self._dRecord[s])
				) for s in self._dStruct['primary']
			])

		# Else, we have a single field primary key
		else:

			# If there is no primary key in the record
			if self._dStruct['primary'] not in self._dRecord:
				raise KeyError(self._dStruct['primary'])

			# Generate the where clause
			sWhere = '`%s` = %s' % (
				self._dStruct['primary'],
				self.escape(
					self._dStruct,
					self._dStruct['primary'],
					self._dRecord[self._dStruct['primary']]
				)
			)

		# If revisions are required
		if self._dStruct['revisions']:

			# Store the old revision
			sRevCurr = self._dRecord[self._dStruct['rev_field']]

			# If updating the revision fails
			if not self._revision_update(self._dStruct):
				return False

			# Use the primary key to fetch the record and return the rev
			sSQL = 'SELECT `%s` FROM `%s`.`%s` WHERE %s' % (
				self._dStruct['rev_field'],
				self._dStruct['db'],
				self._dStruct['table'],
				sWhere
			)

			# Select the cell
			sRev = Commands.select(self._dStruct['host'], sSQL, ESelect.CELL)

			# If there's no such record
			if not sRev:
				return False

			# If it is found, but the revisions don't match up
			if sRev != sRevCurr:
				raise RevisionException(
					self._dRecord[self._dStruct['primary']]
				)

		# If a replace was requested, or all fields have been changed
		if replace or (isinstance(self._dChanged, bool) and self._dChanged):
			lKeys = self._dStruct['tree'].keys()
			lKeys.remove(self._dStruct['primary'])
			dValues = {
				k:(k in self._dRecord and self._dRecord[k] or None)
				for k in lKeys
			}

		# Else we are updating
		else:
			dValues = { k:self._dRecord[k] for k in self._dChanged }

		# Go through each value and create the pairs
		lValues = []
		for f in dValues.keys():
			if f != self._dStruct['primary'] or \
				not self._dStruct['auto_primary']:
				if dValues[f] != None:
					lValues.append('`%s` = %s' % (
						f, self.escape(self._dStruct, f, dValues[f])
					))
				else:
					lValues.append('`%s` = NULL' % f)

		# Generate SQL
		sSQL = 'UPDATE `%s`.`%s` SET %s ' \
				'WHERE %s' % (
					self._dStruct['db'],
					self._dStruct['table'],
					', '.join(lValues),
					sWhere
				)

		# Update the record
		iRes = Commands.execute(self._dStruct['host'], sSQL)

		# If the record wasn't updated for some reason
		if iRes != 1:
			return False

		# If changes are required
		if self._dStruct['changes'] and changes != False:

			# Create the changes record
			dChanges = self.generate_changes(
				self._dOldRecord,
				self._dRecord
			)

			# If Changes requires fields
			if isinstance(self._dStruct['changes'], list):

				# If they weren't passed
				if not isinstance(changes, dict):
					raise ValueError('changes')

				# Else, add the extra fields
				for k in self._dStruct['changes']:
					dChanges[k] = changes[k]

			# If we have a complex primary
			if self._dStruct['complex_primary']:
				sPrimaryKey = '`, `'.join(self._dStruct['primary'])
				sPrimaryValue = ', '.join([
					self.escape(self._dStruct, s, self._dRecord[s]) \
					for s in self._dStruct['primary']
				])
			else:
				sPrimaryKey = self._dStruct['primary']
				sPrimaryValue = self.escape(
					self._dStruct,
					self._dStruct['primary'],
					self._dRecord[self._dStruct['primary']]
				)

			# Generate the INSERT statement
			sSQL = 'INSERT INTO `%s`.`%s_changes` (`%s`, `created`, `items`) ' \
					'VALUES(%s, CURRENT_TIMESTAMP, \'%s\')' % (
						self._dStruct['db'],
						self._dStruct['table'],
						sPrimaryKey,
						sPrimaryValue,
						escape_string(jsonb.encode(dChanges))
					)

			# Create the changes record
			Commands.execute(self._dStruct['host'], sSQL)

			# Reset the old record
			self._dOldRecord = None

		# Clear the changed fields flags
		self._dChanged = {}

		# Return OK
		return True

	@classmethod
	def search(cls,
		fields: dict,
		ids: List[str] | None = None,
		raw: str | List[str] | PyLiteral[True] | None = None,
		orderby: str | List[str] | List[List[str]] = None,
		limit: int | tuple | None = None,
		custom: dict = {}
	) -> List['Record'] | List[dict]:
		"""Search

		Takes values and converts them to something usable by the filter method

		Arguments:
			fields (dict): A dictionary of field names to the values they \
				should match
			raw (bool|str|list): Optional, default returns a list of Records, \
				set to True to return a list of dicts, pass a list to return \
				a list of dicts with only the fields provided, or pass a \
				single string to return a list of just those values
			orderby (str|str[]): A field or fields to order the results by
			limit (int|tuple): The limit and possible starting point
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Raises:
			ValueError

		Returns:
			Record[] | dict[]
		"""

		# Init a new list of fields
		dFields = {}

		# Go through each field passed
		for k,d in fields.items():

			# If we got a string
			if isinstance(d, str):
				d = {'value': d, 'type': 'exact'}

			elif not isinstance(d, dict):
				raise ValueError(k, 'must be dict')

			# Escape special characters
			d['value'] = d['value'].replace('_', r'\_').replace('%', r'\%')

			# If we're looking for an exact match
			if d['type'] == 'exact':
				dFields[k] = d['value']

			# If it starts with
			elif d['type'] == 'start':
				dFields[k] = {'like': '%s%%' % d['value']}

			# If it ends with
			elif d['type'] == 'end':
				dFields[k] = {'like': '%%%s' % d['value']}

			# If it's a custom lookup
			elif d['type'] == 'asterisk':
				dFields[k] = {'like': d['value'].replace('*', '%')}

			# If it's greater than
			elif d['type'] == 'greater':
				dFields[k] = {'gte': d['value']}

			# If it's less than
			elif d['type'] == 'less':
				dFields[k] = {'lte': d['value']}

			# Else
			else:
				raise ValueError(k, 'invalid type')

		# If we have IDs
		if ids:

			# Limit to the IDS and pass the newly generated fields as an
			#	additional filter
			return cls.get(
				ids,
				filter = dFields,
				raw = raw,
				orderby = orderby,
				limit = limit,
				custom = custom
			)

		# Else
		else:

			# Pass the newly generated fields to filter and return the result
			return cls.filter(
				dFields,
				raw = raw,
				orderby = orderby,
				limit = limit,
				custom = custom
			)

	@classmethod
	def table_create(cls, custom: dict = {}) -> bool:
		"""Table Create

		Creates the record's table/collection/etc in the DB

		Arguments:
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Raises:
			ValueError

		Returns:
			bool
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If the 'create' value is missing
		if 'create' not in dStruct:
			raise ValueError(dStruct['table'],
				'Record_MySQL.table_create requires \'create\' in config. ' \
				'i.e. ["key", "field1", "field2", "etc"]'
			)

		# Init the list of fields
		lFields = []

		# If we have a primary key
		if dStruct['primary']:

			# If we have a complex primary key
			if dStruct['complex_primary']:

				# Step through each field
				for s in dStruct['primary']:

					# If it's been added
					if s in dStruct['create']:
						dStruct['create'].remove(s)

				# Get all child node keys
				lNodeKeys = dStruct['tree'].keys()
				lMissing = [
					s for s in lNodeKeys \
					if s not in dStruct['create'] and \
						s not in dStruct['primary']
				]

				# Init the list of indexes with the complex primary key
				lIndexes = [
					'primary key (`%s`)' % '`, `'.join(dStruct['primary'])
				]

				# If we need changes
				if dStruct['changes']:
					dChanges = {
						'key': '`key` (`%s`)' % '`, `'.join(dStruct['primary']),
						'fields': []
					}

				# For code re-use later on
				lKeys = dStruct['primary']

			# Else, we have a single field as primary key
			else:

				# If the primary key is added, remove it
				if dStruct['primary'] in dStruct['create']:
					dStruct['create'].remove(dStruct['primary'])

				# Get all child node keys
				lNodeKeys = dStruct['tree'].keys()
				lMissing = [
					s for s in lNodeKeys \
					if s not in dStruct['create'] and s != dStruct['primary']
				]

				# Init the list of indexes with the primary key
				lIndexes = [ 'primary key (`%s`)' % dStruct['primary'] ]

				# If we need changes
				if dStruct['changes']:
					dChanges = {
						'key': '`key` (`%s`)' % dStruct['primary'],
						'fields': []
					}

				# For code re-use later on
				lKeys = [ dStruct['primary'] ]

			# Step through the primary keys
			for sKey in lKeys:

				# Get the sql special data for the primary
				dSQL = dStruct['tree'][sKey].special(
					'sql', default = {}
				)

				# If it's a string
				if isinstance(dSQL, str):
					dSQL = { 'type': dSQL }

				# Primary key type
				sIDType = 'type' in dSQL and \
					dSQL['type'] or \
					cls._node_to_type(dStruct, sKey)
				sIDOpts = 'opts' in dSQL and dSQL['opts'] or 'not null'

				# Add the line
				lFields.append('`%s` %s %s%s' % (
					sKey,
					sIDType,
					((dStruct['auto_primary'] is True and \
	  					'auto_primary_call' not in dStruct) and \
	  					'auto_increment ' or ''),
					sIDOpts
				))

				# If we need changes, add the field
				if dStruct['changes']:
					dChanges['fields'].append('`%s` %s %s' % (
						sKey,
						sIDType,
						sIDOpts
					))

		# Else, no primary key
		else:

			# Init indexes
			lIndexes = []

			# Get all child node keys
			lNodeKeys = dStruct['tree'].keys()
			lMissing = [
				s for s in lNodeKeys \
				if s not in dStruct['create']
			]

		# If any are missing
		if lMissing:
			raise ValueError(dStruct['table'],
				'Record_MySQL.table_create missing fields `%s` for `%s`.`%s`' %
				( '`, `'.join(lMissing), dStruct['db'], dStruct['table'] )
			)

		# Generate the list of non-primary fields
		for f in dStruct['create']:

			# Get the sql special data
			dSQL = dStruct['tree'][f].special('sql', default={})

			# If it's a string
			if isinstance(dSQL, str):
				dSQL = {'type': dSQL}

			# Add the line
			lFields.append('`%s` %s %s' % (
				f,
				('type' in dSQL and \
					dSQL['type'] or \
					cls._node_to_type(dStruct, f)
				),
				('opts' in dSQL and \
					dSQL['opts'] or \
					(dStruct['tree'][f].optional() and 'null' or 'not null')
				)
			))

		# If there are indexes
		if dStruct['indexes']:

			# Make sure it's a dict
			if not isinstance(dStruct['indexes'], dict):
				raise ValueError(dStruct['table'],
					'Record_MySQL.table_create requires \'indexes\' to be a ' \
					'dict'
				)

			# Loop through the indexes to get the name and fields
			for sName,mFields in dStruct['indexes'].items():

				# If the fields are another dict
				if isinstance(mFields, dict):
					sType = next(iter(mFields))
					sFields = '`%s`' %  (isinstance(mFields[sType], (list,tuple)) and \
										'`,`'.join(mFields[sType]) or \
										(mFields[sType] and mFields[sType] or sName))

				# Else if it's a list
				elif isinstance(mFields, (list,tuple)):
					sType = 'index'
					sFields = ','.join([
						(':' in s and \
							('`%s`(%s)' % tuple(s.split(':'))) or \
							('`%s`' % s)
						) for s in mFields
					])

				# Else, must be a string or None
				else:
					sType = 'index'
					sFields = mFields and \
								(':' in mFields and \
									('`%s`(%s)' % tuple(mFields.split(':'))) or \
									('`%s`' % mFields)
								) or \
								'`%s`' % sName

				# Append the index
				lIndexes.append('%s `%s` (%s)' % (
					sType, sName, sFields
				))

		# Generate the CREATE statement
		lSQL = [
			'CREATE TABLE IF NOT EXISTS `%s`.`%s` (%s, %s) '\
			'ENGINE=%s CHARSET=%s COLLATE=%s' % (
				dStruct['db'],
				dStruct['table'],
				', '.join(lFields),
				', '.join(lIndexes),
				'engine' in dStruct and dStruct['engine'] or 'InnoDB',
				'charset' in dStruct and dStruct['charset'] or 'utf8mb4',
				'collate' in dStruct and dStruct['collate'] or 'utf8mb4_bin'
			)
		]

		# If changes are required
		if dStruct['primary'] and dStruct['changes']:

			# Generate the CREATE statement
			lSQL.append(
				'CREATE TABLE IF NOT EXISTS `%s`.`%s_changes` (' \
				'%s, ' \
				'`created` datetime not null DEFAULT CURRENT_TIMESTAMP, ' \
				'`items` text not null, ' \
				'index %s) ' \
				'ENGINE=%s CHARSET=%s COLLATE=%s' % (
					dStruct['db'],
					dStruct['table'],
					', '.join(dChanges['fields']),
					dChanges['key'],
					'engine' in dStruct and dStruct['engine'] or 'InnoDB',
					'charset' in dStruct and dStruct['charset'] or 'utf8mb4',
					'collate' in dStruct and dStruct['collate'] or 'utf8mb4_bin'
				)
			)

		# Create the table(s) and triggers
		return Commands.execute(dStruct['host'], lSQL)

	@classmethod
	def table_drop(cls, custom: dict = {}) -> bool:
		"""Table Drop

		Deletes the record's table/collection/etc in the DB

		Arguments:
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Generate the DROP statement
		sSQL = 'drop table `%s`.`%s`' % (
					dStruct['db'],
					dStruct['table'],
				)

		# Delete the table
		Commands.execute(dStruct['host'], sSQL)

		# If changes are required
		if dStruct['changes']:

			# Generate the DROP statement
			sSQL = 'drop table `%s`.`%s_changes`' % (
						dStruct['db'],
						dStruct['table'],
					)

			# Delete the table
			Commands.execute(dStruct['host'], sSQL)

		# Return OK
		return True

	@classmethod
	def _triggers_validate(cls, struct):
		"""Triggers Validate

		Validates and cleans up the trigger data

		Arguments:
			struct (dict): The classes' struct data to use

		Returns:
			None
		"""

		# If we have no triggers
		if 'triggers' not in struct or not struct['triggers']:
			raise ValueError(struct['table'], 'No triggers found')

		# Make sure it's a list
		if not isinstance(struct['triggers'], list):
			raise ValueError(struct['table'],
				'"triggers" must be a list of dicts'
			)

		# Step through each trigger
		for i, d in enumerate(struct['triggers']):

			# Make sure it's a dict
			if not isinstance(d, dict):
				raise ValueError(struct['table'],
					'"triggers" must be a list of dicts'
				)

			# Make sure all data is there
			try: evaluate(d, [ 'event', 'sql', 'time' ])
			except ValueError as e:
				raise ValueError(struct['table'],
					[ 'triggers.%i.%s' % (i, f) for f in e.args ],
					'missing'
				)

			# If the event is wrong
			if d['event'].upper() not in [ 'DELETE', 'INSERT', 'UPDATE' ]:
				raise ValueError(struct['table'],
					'triggers.%i.event invalid' % i
				)

			# If the time is wrong
			if d['time'].upper() not in [ 'AFTER', 'BEFORE' ]:
				raise ValueError(struct['table'],
					'triggers.%i.time invalid' % i
				)

			# If the sql is not a string
			if not isinstance(d['sql'], str):

				# Is it a list?
				if isinstance(d['sql'], list):
					d['sql'] = '\n'.join(d['sql'])

				# Else, it's an error
				else:
					raise ValueError(struct['table'],
						'triggers.%i.sql invalid' % i
					)

	@classmethod
	def triggers_create(cls, return_sql = False, custom = {}):
		"""Triggers Create

		Creates the triggers associated with the record's table/collection/etc \
		in the DB. If `return_sql` is set to a struct, that struct is used to \
		generate the SQL and return it instead of being executed. This is for \
		the triggers_reinstall method

		Arguments:
			return_sql (False | struct): Optional, set to a struct to use that \
				struct to generate the SQL
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""

		# Init generated SQL statements
		lSQL = []

		# If we have no struct
		if not return_sql:

			# Get the structure
			dStruct = cls.struct(custom)

			# Validate the data
			cls._triggers_validate(dStruct)

		# Else, use the struct passed
		else:
			dStruct = return_sql

		# Go through the triggers
		for d in dStruct['triggers']:

			# Generate the SQL
			lSQL.append(
				'CREATE TRIGGER `%(db)s`.`%(table)s_%(time)s_%(event)s%(name)s`\n' \
				'%(timeu)s %(eventu)s ON `%(db)s`.`%(table)s`\n' \
				'%(sql)s;' % {
					'db': dStruct['db'],
					'table': dStruct['table'],
					'name': ('name' in d and ('_%s' % d['name']) or ''),
					'time': d['time'],
					'timeu': d['time'].upper(),
					'event': d['event'],
					'eventu': d['event'].upper(),
					'sql': d['sql'] % dStruct
				}
			)

		# If we want to return so we can join this with _drop for _reinstall
		if return_sql:
			return lSQL

		# If we have any triggers to install
		if lSQL:
			try:
				Commands.execute(dStruct['host'], lSQL)
			except ValueError as e:
				if e.args[0] == 1359:
					pass
				else:
					raise e

		# Return OK
		return True

	@classmethod
	def triggers_drop(cls, return_sql = False, custom = {}):
		"""Triggers Drop

		Drops the triggers associated with the record's table/collection/etc \
		in the DB. If `return_sql` is set to a struct, that struct is used to \
		generate the SQL and return it instead of being executed. This is for \
		the triggers_reinstall method

		Arguments:
			return_sql (False | struct): Optional, set to a struct to use that \
				struct to generate the SQL
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""

		# Init generated SQL statements
		lSQL = []

		# If we have no struct
		if not return_sql:

			# Get the structure
			dStruct = cls.struct(custom)

			# Validate the data
			cls._triggers_validate(dStruct)

		# Else, use the struct passed
		else:
			dStruct = return_sql

		# Go through the triggers
		for d in dStruct['triggers']:

			# Generate the SQL
			lSQL.append(
				'DROP TRIGGER IF EXISTS `%(db)s`.`%(table)s_%(time)s_%(event)s%(name)s`'
				% {
					'db': dStruct['db'],
					'table': dStruct['table'],
					'name': ('name' in d and ('_%s' % d['name']) or ''),
					'time': d['time'],
					'event': d['event']
				}
			)

		# If we want to return so we can join this with _create for _reinstall
		if return_sql:
			return lSQL

		# If we have any triggers to drop
		if lSQL:
			Commands.execute(dStruct['host'], lSQL)

		# Return OK
		return True

	@classmethod
	def triggers_recreate(cls, custom = {}):
		"""Triggers Re-Create

		Drops the triggers associated with the record's table/collection/etc \
		in the DB, then creates them again. Locks the table so no rows get in \
		while this is happening

		Arguments:
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""

		# Get the struct
		dStruct = cls.struct(custom)

		# Validate the data
		cls._triggers_validate(dStruct)

		# Init the SQL by locking the table
		lSQL = [ 'LOCK TABLES `%(db)s`.`%(table)s` WRITE' % dStruct ]

		# Call the _drop method to generate the DROP TRIGGER
		lSQL.extend(
			cls.triggers_drop(return_sql = dStruct)
		)

		# Call the _create method to generate the CREATE TRIGGER
		lSQL.extend(
			cls.triggers_create(return_sql = dStruct)
		)

		# Unlock the table
		lSQL.append('UNLOCK TABLES')

		# If there's anything (LOCK / UNLOCK statements don't count), execute it
		if len(lSQL) > 2:
			Commands.execute(dStruct['host'], lSQL)

		# Return OK
		return True

	@classmethod
	def update_field(cls,
		field: str,
		value: any,
		key: any | List[any] | None = None,
		index: str | None = None,
		filter: dict | None = None,
		custom: dict = {}
	) -> int:
		"""Updated Field

		Updates a specific field to the value for an ID, many IDs, or the \
		entire table

		Arguments:
			field (str): The name of the field to update
			value (any): The value to set the field to
			key (any): Optional ID(s) to filter by
			index (str): Optional name of the index to use instead of primary
			filter (dict): Optional filter list to decide what records get \
				updated
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			uint -- Number of records altered
		"""

		# Don't allow index
		if index is not None:
			raise Exception(
				'index not a valid argument in Record_MySQL.update_field'
			)

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If the field doesn't exist
		if field not in dStruct['tree']:
			raise ValueError('%s not a valid field' % field)

		# Init the where fields
		lWhere = []

		# If the primary key was passed
		if key is not None:

			# If we have a complex primary
			if dStruct['complex_primary']:
				raise RuntimeError('key',
					'`key` can not be used with complex primary keys. Use ' \
					'`filter` instead'
				)

			# Add the primary to the where clause
			lWhere.append('`%s` %s' % (
				dStruct['primary'],
				cls.process_value(dStruct, dStruct['primary'], key)
			))

		# If there's an additional filter
		if filter:

			# If we only have one
			if isinstance(filter, dict):
				lWhere.append(' AND '.join([
					'`%s` %s' % (n, cls.process_value(dStruct, n, v)) \
					for n,v in filter.items()
				]))

			# If we have multiple
			elif isinstance(filter, list):
				lWhere.append('(%s)' % ') OR ('.join(
					[ ' AND '.join([
						'`%s` %s' % (n, cls.process_value(dStruct, n, v)) \
						for n,v in d.items()
					]) for d in filter ]
				))

			# Else, invalid filter
			else:
				raise ValueError('filter', 'must be a dict or dict[]')

		# Generate the SQL to update the field
		sSQL = 'UPDATE `%s`.`%s` ' \
				'SET `%s` = %s ' \
				'%s' % (
			dStruct['db'], dStruct['table'],
			field, cls.escape(dStruct, field, value),
			lWhere and ('WHERE %s' % ' AND '.join(lWhere)) or ''
		)

		# Update all the records and return the number of rows changed
		return Commands.execute(dStruct['host'], sSQL)

	@classmethod
	def uuid(cls, custom: dict = {}) -> str:
		"""UUID

		Returns a universal unique ID

		Arguments:
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			str
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Get the UUID
		return Commands.select(dStruct['host'], 'select uuid()', ESelect.CELL)

# Register the module with the Base
Record_Base.register_type('mysql', sys.modules[__name__])