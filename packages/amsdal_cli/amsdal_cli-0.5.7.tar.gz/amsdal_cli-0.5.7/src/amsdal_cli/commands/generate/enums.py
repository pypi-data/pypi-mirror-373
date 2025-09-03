from enum import Enum

MODEL_JSON_FILE = 'model.json'
MODEL_PY_FILE = 'model.py'
FIXTURES_JSON_FILE = 'fixtures.json'
FIXTURES = 'fixtures'


class HookName(str, Enum):
    """
    Enum representing different hook names used in the application lifecycle.

    Attributes:
        PRE_INIT (str): Hook name for pre-initialization.
        POST_INIT (str): Hook name for post-initialization.
        PRE_CREATE (str): Hook name for pre-creation.
        POST_CREATE (str): Hook name for post-creation.
        PRE_UPDATE (str): Hook name for pre-update.
        POST_UPDATE (str): Hook name for post-update.
        PRE_DELETE (str): Hook name for pre-deletion.
        POST_DELETE (str): Hook name for post-deletion.
    """

    PRE_INIT = 'pre_init'
    POST_INIT = 'post_init'
    PRE_CREATE = 'pre_create'
    POST_CREATE = 'post_create'
    PRE_UPDATE = 'pre_update'
    POST_UPDATE = 'post_update'
    PRE_DELETE = 'pre_delete'
    POST_DELETE = 'post_delete'


class ModifierName(str, Enum):
    """
    Enum representing different modifier names used in the application.

    Attributes:
        CONSTRUCTOR (str): Modifier name for constructor.
        DISPLAY_NAME (str): Modifier name for display name.
        VERSION_NAME (str): Modifier name for version name.
    """

    CONSTRUCTOR = 'constructor'
    DISPLAY_NAME = 'display_name'
    VERSION_NAME = 'version_name'


class AttributeType(str, Enum):
    """
    Enum representing different attribute types used in the application.

    Attributes:
        STRING (str): Attribute type for string values.
        NUMBER (str): Attribute type for numeric values.
        INTEGER (str): Attribute type for integer values.
        BOOLEAN (str): Attribute type for boolean values.
        BELONGS_TO (str): Attribute type for belongs-to relationships.
        HAS_MANY (str): Attribute type for has-many relationships.
        DICT (str): Attribute type for dictionary values.
    """

    STRING = 'string'
    NUMBER = 'number'
    INTEGER = 'integer'
    BOOLEAN = 'boolean'
    BELONGS_TO = 'belongs-to'
    HAS_MANY = 'has-many'
    DICT = 'dict'


class JsonType(str, Enum):
    """
    Enum representing different JSON types used in the application.

    Attributes:
        STRING (str): JSON type for string values.
        NUMBER (str): JSON type for numeric values.
        INTEGER (str): JSON type for integer values.
        BOOLEAN (str): JSON type for boolean values.
        ARRAY (str): JSON type for array values.
        DICT (str): JSON type for dictionary values.
    """

    STRING = 'string'
    NUMBER = 'number'
    INTEGER = 'integer'
    BOOLEAN = 'boolean'
    ARRAY = 'array'
    DICT = 'dictionary'


class OptionName(str, Enum):
    """
    Enum representing different option names used in the application.

    Attributes:
        INDEX (str): Option name for index.
        DEFAULT (str): Option name for default value.
        REQUIRED (str): Option name for required attribute.
        UNIQUE (str): Option name for unique attribute.
    """

    INDEX = 'index'
    DEFAULT = 'default'
    REQUIRED = 'required'
    UNIQUE = 'unique'


class TestType(str, Enum):
    """
    Enum representing different test types used in the application.

    Attributes:
        UNIT (str): Test type for unit tests.
    """

    UNIT = 'unit'


class TestDataType(str, Enum):
    """
    Enum representing different test data types used in the application.

    Attributes:
        RANDOM (str): Test data type for random data.
        DYNAMIC (str): Test data type for dynamic data.
        DUMMY (str): Test data type for dummy data.
    """

    RANDOM = 'random'
    DYNAMIC = 'dynamic'
    DUMMY = 'dummy'
