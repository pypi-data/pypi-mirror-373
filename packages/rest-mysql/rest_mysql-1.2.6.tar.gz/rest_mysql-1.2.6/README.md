# rest_mysql
[![pypi version](https://img.shields.io/pypi/v/rest_mysql.svg)](https://pypi.org/project/rest_mysql) ![MIT License](https://img.shields.io/pypi/l/rest_mysql.svg)

Stand alone version of Record_MySQL from Rest-OC to facilitate updating code to
newer librairies. Since forking off of Rest-OC numerous improvements and bug
fixes have been done.

See [Releases](https://github.com/ouroboroscoding/rest_mysql/blob/main/releases.md)
for changes from release to release.

[Full Documentation](https://github.com/ouroboroscoding/rest_mysql/blob/main/documentation.md)

## Install

### Requires
rest_mysql requires python 3.10 or higher

### Install via pip
```bash
pip install rest_mysql
```

## Updating from Rest-OC
Instead of pulling Record_MySQL from RestOC as we did in the past, change any
references to rest_mysql

Old:
```python
from RestOC import Record_MySQL
from RestOC.Record_MySQL import db_create, Record
from RestOC.Record_Base import register_type
```

New:
```python
from rest_mysql import Record_MySQL
from rest_mysql.Record_MySQL import db_create, Record
from rest_mysql.Record_Base import register_type
```

## Binary UUID and UUIDv4

If you're using `uuid` or `uuid4` [define](https://pypi.org/project/define-oc/)
types and you run into problems with UUID_TO_BIN and BIN_TO_UUID, you will need
to install the functions, or an alias

### Note

Before continuing, I would suggest switching to `tuuid` or `tuuid4` as these
represent trimmed UUIDs, which can be turned to binary and back without the use
of UUID_TO_BIN or BIN_TO_UUID. If you absolutely must have full UUIDs, then
choose from the below server types to continue fixing the issue.

### MySQL

MySQL provides the functions, but in order for `rest_mysql` to be supportive of
all system, it defaults to assuming the function is part of the database schema.
To solve this, make aliases to the global functons

```python
from rest_mysql.Record_MySQL import Commands

db = 'your_db_name'
Commands.execute('primary', [

	"CREATE FUNCTION `%s`.`BIN_TO_UUID`(b BINARY(16))\n" \
	"RETURNS CHAR(36) DETERMINISTIC\n" \
	"BEGIN\n" \
	"	return BIN_TO_UUID(b);\n" \
	"END" % db,

	"CREATE FUNCTION `%s`.`UUID_TO_BIN`(uuid CHAR(36))\n" \
	"RETURNS BINARY(16) DETERMINISTIC\n" \
	"BEGIN\n" \
	"	RETURN UUID_TO_BIN(uuid);\n" \
	"END" % db
])
```

### MariaDB

MariaDB does not provide UUID_TO_BIN and BIN_TO_UUID as it has its own uuid type
which doesn't support the standard sql way of storing binary UUIDs. You can add
the functions to the database schema like so

```python
from rest_mysql.Record_MySQL import Commands

db = 'your_db_name'
Commands.execute('primary', [

	"CREATE FUNCTION `%s`.`BIN_TO_UUID`(b BINARY(16))\n" \
	"RETURNS CHAR(36) DETERMINISTIC\n" \
	"BEGIN\n" \
	"	DECLARE hexStr CHAR(32);\n" \
	"	SET hexStr = HEX(b);\n" \
	"	RETURN LOWER(CONCAT(" \
			"SUBSTR(hexStr, 1, 8), '-', " \
			"SUBSTR(hexStr, 9, 4), '-', " \
			"SUBSTR(hexStr, 13, 4), '-', " \
			"SUBSTR(hexStr, 17, 4), '-', " \
			"SUBSTR(hexStr, 21)" \
		"));\n" \
	"END" % db,

	"CREATE FUNCTION `%s`.`UUID_TO_BIN`(uuid CHAR(36))\n" \
	"RETURNS BINARY(16) DETERMINISTIC\n" \
	"BEGIN\n" \
		"RETURN UNHEX(REPLACE(uuid, '-', ''));\n" \
	"END" % db
])
```