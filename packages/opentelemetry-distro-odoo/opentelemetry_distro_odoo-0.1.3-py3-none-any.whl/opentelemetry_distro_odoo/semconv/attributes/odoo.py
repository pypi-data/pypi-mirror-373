ODOO_UID = "odoo.uid"
"""
The user id of the current user.
"""

ODOO_CIDS = "odoo.cids"
"""
The company ids of the current user.
"""

ODOO_RECORD_IDS = "odoo.record.ids"
"""
All the `ids` of the record. (ids field)
"""

ODOO_MODEL_NAME = "odoo.record.name"
"""
The name of the record. (_name field)
"""

ODOO_CURSOR_MODE = "odoo.cursor_mode"
"""
The cursor mode used by the call.
Introduced in 18.0 Odoo can have a read-only cursor or a read-write cursor
This is defined with the @api.readonly decorator. For previous version set this attribute to "rw" by default
"""

ODOO_CURSOR_DB = "odoo.database"
"""
The database used by the cursor
"""

ODOO_MODEL_FUNCTION_NAME = "odoo.record.function"
"""
The name of the function called on the record.
"""
ODOO_ATTR_TYPE = "type"
"""
A generique attribute when a type of the metrics is necessary
"""
