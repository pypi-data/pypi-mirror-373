# coding=utf8
""" Record Base Module

The base concept for all records stored in any sort of DB
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2018-11-11"

# Ouroboros imports
from define import Tree
from tools import clone, combine, merge
import jsonb

# Python imports
import abc
from hashlib import md5
from typing import List, Literal

# The global DB prefix
__msPrepend = ''

# The list of registered DB types
__mlTypes = {}

def db_prepend(pre = None):
	"""DB Prepend

	Gets or sets the global prefix for all DBs, useful for testing/development

	Arguments:
		pre (str): The prefix to store

	Returns:
		str|None
	"""

	# If a prefix was passed
	if pre:
		global __msPrepend
		__msPrepend = pre

	# Else return what we have
	else:
		return __msPrepend

def get_type(type_):
	"""Get Type

	Returns the module used to work with the specific type

	Arguments:
		type_ (str): The name of the type of DB

	Returns:
		module
	"""
	return __mlTypes[type_]

def register_type(type_, module_):
	"""Register Type

	Sets the class instance used for a specific DB type

	Arguments:
		type_ (str): The name used for the type of DB
		module_ (module): The module being registered

	Throws:
		ValueError

	Returns:
		None
	"""

	# Go through each type and check for an add_host, db_create, and db_drop
	#	function
	try: getattr(module_, 'add_host')
	except AttributeError:
		raise ValueError("%s does not have a valid add_host function" % type_)
	try: getattr(module_, 'db_create')
	except AttributeError:
		raise ValueError("%s does not have a valid db_create function" % type_)
	try: getattr(module_, 'db_drop')
	except AttributeError:
		raise ValueError("%s does not have a valid db_drop function" % type_)

	# If we got no exceptions, store the module
	global __mlTypes
	__mlTypes[type_] = module_

class DuplicateException(Exception):
	"""DuplicateException class

	Used for raising issues with duplicate records
	"""
	pass

class RevisionException(Exception):
	"""Revision Exception

	Raised if a record can not be updated do to Revision failure
	"""
	pass

class Record(abc.ABC):
	"""Record

	The base class for all child record classes
	"""

	def __init__(self, record={}, custom = {}):
		"""Constructor

		Initialises the instance and returns it

		Arguments:
			record (dict): The record data
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			Record
		"""

		# Fetch the record structure
		self._dStruct = self.struct(custom)

		# If we received data
		if record:

			# Validate it
			if not self._dStruct['tree'].valid(record, False):
				raise ValueError(self._dStruct['tree'].validation_failures)

		# Store the data and reset the changed flags
		self._dRecord = self._dStruct['tree'].clean(record)
		self._dChanged = {}

		# If we need to keep changes
		if self._dStruct['changes']:
			self._dOldRecord = None

	def __contains__(self, field):
		"""__contains__

		Python magic method for checking a key exists in a dict like object

		Arguments:
			field (str): The field to check for

		Returns:
			bool
		"""
		return field in self._dRecord

	def __delitem__(self, field):
		"""__delitem__

		Python magic method for deleting a key from a dict like object

		Arguments:
			field (str): The field to delete

		Raises:
			KeyError

		Returns:
			None
		"""
		self.field_delete(field)

	def __getitem__(self, field):
		"""__getitem__

		Python magic method for getting a key from a dict like object

		Arguments:
			field (str): The field to return

		Raises:
			KeyError

		Returns:
			mixed
		"""
		return self._dRecord[field]

	def __setitem__(self, field, val):
		"""__setitem__

		Python magic method for setting a key in a dict like object

		Arguments:
			field (str): The field to set
			val (mixed): The value of the field

		Raises:
			KeyError
			ValueError

		Returns:
			None
		"""
		self.field_set(field, val)

	def __str__(self):
		"""__str__

		Python magic method to return a string for the instance

		Returns:
			str
		"""
		return str(self._dRecord)

	@classmethod
	def _revision_init(cls, record: dict, struct: dict):
		"""Revision Init

		Adds the initial revision to the record

		Arguments:
			record (dict): The record to be inserted
			struct (dict): The structure of the record
		"""

		# Remove the _rev value so we don't include it in the MD5
		if struct['rev_field'] in record:
			del record[struct['rev_field']]

		# Generate and set the revision
		record[struct['rev_field']] = '1-%s' % \
			md5(jsonb.encode(record)).hexdigest()

	def _revision_update(self, struct: dict) -> bool:
		"""Revision Update

		Updates an existing revision

		Arguments:
			record (dict): The record to add / update the revision
			struct (dict): The structure for the record

		Returns:
			bool
		"""

		# Remove and store the existing revision
		sRev = self._dRecord[struct['rev_field']]
		del self._dRecord[struct['rev_field']]

		# Split it into version and hash
		sVer, sHash = sRev.split('-')

		# Generate a new hash from the record data
		sMD5 = md5(jsonb.encode(self._dRecord)).hexdigest()

		# If the old and new hash don't match
		if sMD5 != sHash:

			# Update the revision
			self._dRecord[struct['rev_field']] = '%d-%s' % \
				(int(sVer)+1, sMD5)

			# Flag the revision field as changed
			if self._dChanged != True:
				self._dChanged[struct['rev_field']] = True

			# Return OK
			return True

		# The record hasn't actually changed
		return False

	@classmethod
	@abc.abstractmethod
	def add_changes(cls, key, changes, customer={}):
		"""Add Changes

		Adds a record to the tables associated _changes table. Useful for \
		Record types that can't handle multiple levels and have children \
		tables that shouldn't be updated for every change in a single record

		Arguments:
			key (mixed): The ID of the record the change is associated with
			changes (dict): The dictionary of changes to add
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "add_changes" method')

	@classmethod
	@abc.abstractmethod
	def append(cls, key, array, item, custom = {}):
		"""Append

		Adds an item to a given array/list for a specific record

		Arguments:
			key (mixed): The ID of the record to append to
			array (str): The name of the field with the array
			item (mixed): The value to append to the array
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "append" method')

	def changed(self, field):
		"""Changed

		Returns whether a specific field has been changed, might give a false \
		positive if the entire record is marked as to be replaced

		Arguments:
			field (str): The field to check

		Returns:
			bool
		"""
		return self._dChanged is True or field in self._dChanged

	def changes(self):
		"""Changes

		Returns the list of changed fields

		Returns:
			list
		"""
		if self._dChanged is True:
			return True
		else:
			return self._dChanged.keys()

	@classmethod
	@abc.abstractmethod
	def config(cls):
		"""Config

		Returns the configuration data associated with the record type

		Returns:
			dict
		"""
		raise NotImplementedError('Must implement the "config" method')

	@classmethod
	@abc.abstractmethod
	def contains(cls, key, array, item, custom = {}):
		"""Contains

		Checks if a specific item exist inside a given array/list

		Arguments:
			key (mixed): The ID of the record to check
			array (str): The name of the field with the array
			item (mixed): The value to check for in the array
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "contains" method')

	@classmethod
	@abc.abstractmethod
	def count(cls, key, index = None, filter=None, custom = {}):
		"""Count

		Returns the number of records associated with index or filter

		Arguments:
			keys (mixed): The ID to check
			index (str): Used as the index instead of the primary key
			filter (dict): Additional filter
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "count" method')

	@abc.abstractmethod
	def create(self, conflict='error', changes = None):
		"""Create

		Adds the record to the DB and returns the primary key

		Arguments:
			conflict (str): Must be one of 'error', 'replace', or 'update'
			changes (dict): Data needed to store a change record, is
				dependant on the 'changes' config value

		Returns:
			mixed|None
		"""
		raise NotImplementedError('Must implement the "create" method')

	@classmethod
	@abc.abstractmethod
	def create_many(cls, records, conflict='error', custom = {}):
		"""Create Many

		Inserts multiple records at once

		Arguments:
			records (Record_Base.Record[]): A list of Record instances to insert
			conflict (str): What to do on a conflict, Record type specific
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			uint
		"""
		raise NotImplementedError('Must implement the "create_many" method')

	@abc.abstractmethod
	def delete(self, changes = None):
		"""Delete

		Deletes the record represented by the instance

		Arguments:
			changes (dict): Data needed to store a change record, is
				dependant on the 'changes' config value

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "delete" method')

	@classmethod
	@abc.abstractmethod
	def delete_get(cls, key, index = None, custom = {}):
		"""Delete Get

		Deletes one or many records by ID or index and returns how many were \
		found/deleted

		Arguments:
			key (mixed|mixed[]): The ID(s) to delete or None for all records
			index (str): Used as the index instead of the primary key
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Return:
			int
		"""
		raise NotImplementedError('Must implement the "delete_get" method')

	@classmethod
	@abc.abstractmethod
	def exists(cls, key, index = None, custom = {}):
		"""Exists

		Returns the ID (primary key) of the record for the specified ID or \
		unique index value found, else False if no record is found

		Arguments:
			key (mixed): The ID to check
			index (str): Used as the index instead of the primary key
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			mixed|False
		"""
		raise NotImplementedError('Must implement the "exists" method')

	def field_delete(self, field):
		"""Field Delete

		Deletes a specific field from a record (used by __delitem__)

		Arguments:
			field (str): The field to delete

		Raises:
			KeyError

		Returns:
			self
		"""

		# If the field is not valid for the record
		if field not in self._dStruct['tree']:
			raise KeyError(field)

		# If the field doesn't exist in the data there's nothing to do
		if field not in self._dRecord:
			return self

		# If the field isn't optional
		if not self._dStruct['tree'][field].optional():
			raise ValueError([[field, 'missing']])

		# Remove the field from the document
		del self._dRecord[field]

		# Flag the entire document as needing to be updated
		self._dChanged = True

		# Return ok
		return self

	def field_get(self, field, default=None):
		"""Field Get

		Returns a specific field, if it's not found, returns the default

		Arguments:
			field (str): The field to get
			default (mixed): Returned if the field doesn't exist

		Returns:
			mixed
		"""

		# If the field doesn't exist
		if field not in self._dRecord:
			return default

		# Return the field
		return self._dRecord[field]

	def field_set(self, field, val):
		"""Field Set

		Sets a specific field in a record (used by __setitem__)

		Arguments:
			field (str): The name of the field to set
			val (mixed): The value to set the field to

		Raises:
			ValueError: field or value is invalid

		Returns:
			self for chaining
		"""

		# If the field is not valid for the record
		if field not in self._dStruct['tree']:
			raise ValueError([
				[ '%s.%s' % (self._dStruct['tree'].name, field), 'unknown' ]
			])

		# If the field hasn't changed
		if field in self._dRecord and val == self._dRecord[field]:
			return self

		# If the value isn't valid for the field
		if not self._dStruct['tree'][field].valid(
			val,
			level = [ self._dStruct['tree'].name, field ]
		):
			raise ValueError(self._dStruct['tree'][field].validation_failures)

		# If we need to keep changes
		if self._dStruct['changes']:
			if self._dOldRecord is None:
				self._dOldRecord = clone(self._dRecord)

		# If the value is not None, store it after cleaning it
		if val is not None:
			self._dRecord[field] = self._dStruct['tree'][field].clean(val)
		else:
			self._dRecord[field] = None

		# If we still have a dict for changes (not a total replace)
		if isinstance(self._dChanged, dict):
			self._dChanged[field] = True

		# Allow chaining
		return self

	def fields_set(self, fields: dict):
		"""Fields Set

		Sets numerous fields in a record

		Arguments:
			fields (dict): The field / value pairs to set

		Raises:
			ValueError: field(s) or value(s) are invalid
		"""

		# Init errors
		lErrors = []

		# Step through the fields
		for f,v in fields.items():

			# If the field is not valid for the record
			if f not in self._dStruct['tree']:
				lErrors.append(
					[ '%s.%s' % (self._dStruct['tree'], f), 'unknown' ]
				)

			# If the field hasn't changed, loop around
			if f in self._dRecord and v == self._dRecord[f]:
				continue

			# If the value isn't valid for the f
			if not self._dStruct['tree'][f].valid(
				v, level = [ self._dStruct['tree'].name, f ]
			):
				lErrors.extend(self._dStruct['tree'][f].validation_failures)
				continue

			# If we need to keep changes
			if self._dStruct['changes']:
				if self._dOldRecord is None:
					self._dOldRecord = clone(self._dRecord)

			# If the value is not None, store it after cleaning it
			if v is not None:
				self._dRecord[f] = self._dStruct['tree'][f].clean(v)
			else:
				self._dRecord[f] = None

			# If we still have a dict for changes (not a total replace)
			if isinstance(self._dChanged, dict):
				self._dChanged[f] = True

		# If there's any errors
		if lErrors:
			raise ValueError(lErrors)

	@classmethod
	@abc.abstractmethod
	def filter(cls,
		fields,
		raw = None,
		distinct = False,
		orderby = None,
		limit = None,
		custom = {}
	):
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

		Returns:
			Record[]|dict[]
		"""
		raise NotImplementedError('Must implement the "filter" method')

	@classmethod
	def generate_changes(cls, old, new):
		"""Generate Changes

		Generates the list of changes between two records

		Arguments:
			old (dict): Old record
			new (dict): New record

		Returns:
			dict|None
		"""

		# If we are dealing with a dict
		if isinstance(old, dict):

			# If the new is not also a dict
			if not isinstance(new, dict):
				return { 'old': old, 'new': new }

			# Both are dicts, create a new dict to return
			dRet = {}

			# Get the length of keys in old
			iOldLen = len(old.keys())

			# Store the keys from new and get the length
			lNewKeys = list(new.keys())
			iNewLen = len(lNewKeys)

			# Start checking keys from old
			for k in old:

				# If the key doesn't exist in new
				if k not in new:
					dRet[k] = { 'old': old[k], 'new': None }
					continue

				# It exists in both so pass the two along and remove the key
				#	from the new list
				dTemp = cls.generate_changes(old[k], new[k])
				lNewKeys.remove(k)

				# If there's a value, store it
				if dTemp: dRet[k] = dTemp

			# If there's any keys left in the new list
			if lNewKeys:
				for k in lNewKeys:
					dRet[k] = { 'old': None, 'new':  new[k] }

			# If the number of keys different match all data, set everything as
			#	changed
			iMaxKeys = iOldLen > iNewLen and iOldLen or iNewLen
			if len(dRet.keys()) >= iMaxKeys:
				return { 'old': old, 'new': new }

			# Return the changes if there are any
			if dRet: return dRet

		# Else if we are dealing with a list
		elif isinstance(old, list):

			# If the new is not also a list
			if not isinstance(new, list):
				return { 'old': old, 'new': new }

			# Both are lists, create a new dict to return
			dRet = {}

			# Get the length of the old and new
			iOldLen = len(old)
			iNewLen = len(new)

			# Start going through the indexes of the old
			for i in range(iOldLen):

				# If it's not in the new
				if i >= iNewLen:
					dRet[str(i)] = { 'old': old[i], 'new': None }
					continue

				# It exists in both so pass the two along
				dTemp = cls.generate_changes(old[i], new[i])

				# If there's a value, store it
				if dTemp: dRet[str(i)] = dTemp

			# If there's more new indexes than old
			if iNewLen > iOldLen:
				for i in range(iOldLen, iNewLen):
					dRet[str(i)] = { 'old': None, 'new': new[i] }

			# If the number of indexes different match all data, set everything
			#	as changed
			iMaxKeys = iOldLen > iNewLen and iOldLen or iNewLen
			if len(dRet.keys()) >= iMaxKeys:
				return { 'old': old, 'new': new }

			# Return the changes if there are any
			if dRet: return dRet

		# Else it's a single value
		else:

			# If the new is a dict or list or the values don't match
			if isinstance(new, (dict,list)) or new != old:
				return { 'old': old, 'new': new }

		# No changes
		return None

	@classmethod
	def generate_config(cls,
		tree: Tree,
		special: str = 'db',
		override = None
	):
		"""Generate Config

		Generates record specific config based on the Format-OC tree passed

		Arguments:
			tree (define.Tree): the tree associated with the record type
			special (str): The special section used to identify the child info
			override (dict): Used to override any data from the tree

		Returns:
			dict
		"""

		# Combine the dicts
		dRet = combine({
			'auto_primary': True,
			'changes': False,
			'db': 'test',
			'host': 'records',
			'indexes': {},
			'table': tree.name,
			'primary': '_id',
			'rev_field': '_rev',
			'revisions': False,
			'tree': tree
		}, tree.special(special, default={}))

		# If there's an override
		if override:

			# Make sure it's a dict before merging it with the current config
			if isinstance(override, dict):
				merge(dRet, override)

			# Raise an error if the argument is invalid
			else:
				raise ValueError(
					'Record_Base.generate_config.override must be a dict'
				)

		# Return the values
		return dRet

	@classmethod
	@abc.abstractmethod
	def get(cls,
		key = None,
		index = None,
		filter = None,
		match = None,
		raw = None,
		distinct = False,
		orderby = None,
		limit = None,
		custom = {}
	):
		"""Get

		Returns records by ID or index, can also be given an extra filter

		Arguments:
			key (mixed|mixed[]): The ID(s) to fetch from the table
			index (str): Index to use instead of primary key
			filter (dict): Additional filter
			match (tuple): Name/Match filter
			raw (bool|list): Return raw data (dict) for all or a set list of \
				fields
			distinct (bool): Only return distinct data
			orderby (str|str[]): A field or fields to order the results by
			limit (int|tuple): The limit and possible starting point
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			Record|Record[]|dict|dict[]
		"""
		raise NotImplementedError('Must implement the "get" method')

	@classmethod
	@abc.abstractmethod
	def get_changes(cls, key, orderby = None, custom = {}):
		"""Get Changes

		Returns the changes record associated with the primary record and \
		table. Used by Record types that have the 'changes' flag set.

		Arguments:
			key (mixed): The of the primary record to fetch changes for
			orderby (str|str[]): A field or fields to order the results by
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			dict
		"""
		raise NotImplementedError('Must implement the "get_changes" method')

	@classmethod
	def keys(cls, without: List[str] | Literal['_'] | None = None) -> List[str]:
		"""Keys

		Returns the keys of the fields available in the record

		Arguments:
			without (list), Optional, can be passed a list of list of keys to \
				remove from the list before returning, or the '_' character \
				to indicate removing all fields that start with an underscore

		Returns:
			str[]
		"""

		# Get the structure
		dStruct = cls.struct()

		# Get all the keys
		lKeys = dStruct['tree'].keys()

		# If we got no `without`
		if without is None:
			return lKeys

		# If we got '_'
		if without == '_':
			return [ s for s in lKeys if s[0] != '_' ]

		# If we got a list
		if isinstance(without, list):
			return [ s for s in lKeys if s not in without ]

	def record(self, fields = False):
		"""Record

		Returns the record data as a dict

		Arguments:
			fields (list): Optional list of fields to return, if not set,
							returns all fields

		Returns:
			dict
		"""

		# If no specific fields requested
		if not fields:
			dRet = clone(self._dRecord)

		# Else, get each requested field and return
		else:
			dRet = {f:self._dRecord[f] for f in fields if f in self._dRecord}

		# Clone the results and return
		return clone(dRet)

	@classmethod
	@abc.abstractmethod
	def remove(cls, key, array, index, custom = {}):
		"""Remove

		Removes an item from a given array/list for a specific record

		Arguments:
			key (mixed): The ID of the record to remove from
			array (str): The name of the field with the array
			index (uint): The index of the array to remove
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "remove" method')

	@abc.abstractmethod
	def save(self, replace = False, changes = None):
		"""Save

		Updates the record in the DB and returns true if anything has changed, \
		or a new revision number of the record is revisionable

		Arguments:
			replace (bool): If true, replace all fields instead of updating
			changes (dict): Data needed to store a change record, is
				dependant on the 'changes' config value

		Returns:
			bool|str
		"""
		raise NotImplementedError('Must implement the "save" method')

	@classmethod
	def struct(cls, custom = {}):
		"""Struct

		Returns structure info for the record based on the DB and Tree

		Arguments:
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			dict
		"""

		# Get the config values associated with the Child record
		dConfig = clone(cls.config())

		# If the host value is overriden
		if 'host' in custom:
			dConfig['host'] = custom['host']

		# Add the global prefix
		dConfig['db'] = db_prepend() + dConfig['db']

		# If we received an append value
		if 'append' in custom:
			dConfig['db'] = "%s_%s" % (dConfig['db'], custom['append'])

		# Return the structure
		return dConfig

	@classmethod
	@abc.abstractmethod
	def table_create(cls, custom = {}):
		"""Table Create

		Creates the record's table/collection/etc in the DB

		Arguments:
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "table_create" method')

	# tableDelete static method
	@classmethod
	@abc.abstractmethod
	def table_drop(cls, custom = {}):
		"""Table Drop

		Deletes the record's table/collection/etc in the DB

		Arguments:
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "table_drop" method')

	@classmethod
	def table_name(cls):
		"""Table Name

		Returns the name for the given record child class

		Returns:
			str
		"""
		return cls.struct()['table']

	@classmethod
	@abc.abstractmethod
	def update_field(cls,
		field,
		value,
		key = None,
		index = None,
		filter = None
	):
		"""Updated Field

		Updates a specific field to the value for an ID, many IDs, or the \
		entire table. Returns the number of records altered

		Arguments:
			field (str): The name of the field to update
			value (mixed): The value to set the field to
			key (mixed): Optional ID(s) to filter by
			index (str): Optional name of the index to use instead of primary
			filter (dict): Optional filter list to decide what records get \
				updated

		Returns:
			uint
		"""
		raise NotImplementedError('Must implement the "update_field" method')

	@classmethod
	@abc.abstractmethod
	def uuid(custom = {}):
		"""UUID

		Returns a universal unique ID

		Arguments:
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			str
		"""
		raise NotImplementedError('Must implement the "uuid" method')
