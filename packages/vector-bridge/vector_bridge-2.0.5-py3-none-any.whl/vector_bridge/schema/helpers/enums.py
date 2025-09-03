from enum import Enum


class GPTActions(str, Enum):
    SEARCH = "SEARCH"
    SIMILAR = "SIMILAR"
    SUMMARY = "SUMMARY"
    JSON = "JSON"
    CODE_EXEC = "CODE_EXEC"
    FORWARD_TO_AGENT = "FORWARD_TO_AGENT"
    OTHER = "OTHER"


class UserType(str, Enum):
    OWNER = "OWNER"
    USER = "USER"
    CLIENT = "CLIENT"
    AI = "AI"


class ResponseFormat(str, Enum):
    TEXT = "TEXT"
    JSON = "JSON"


class FunctionCallChainExecutionOrder(str, Enum):
    BEGINNING = "BEGINNING"
    END = "END"


class CreateUserType(str, Enum):
    OWNER = "OWNER"
    AGENT = "AGENT"


class UserStatus(str, Enum):
    UNCONFIRMED = "UNCONFIRMED"
    CONFIRMED = "CONFIRMED"
    DISABLED = "DISABLED"


class PolicyType(str, Enum):
    CHAT = "CHAT"
    MESSAGE = "MESSAGE"
    ORGANIZATION = "ORGANIZATION"
    USER = "USER"


class MessageType(str, Enum):
    TEXT = "TEXT"


class PromptKey(str, Enum):
    SYSTEM = "system_prompt"
    MESSAGE = "message_prompt"
    KNOWLEDGE = "knowledge_prompt"


class OpenAIKey(str, Enum):
    MAX_TOKENS = "max_tokens"
    FREQUENCY_PENALTY = "frequency_penalty"
    PRESENCE_PENALTY = "presence_penalty"
    TEMPERATURE = "temperature"


class OverridesKey(str, Enum):
    MODEL = "model"
    MAX_TOKENS = "max_tokens"
    FREQUENCY_PENALTY = "frequency_penalty"
    PRESENCE_PENALTY = "presence_penalty"
    TEMPERATURE = "temperature"


class WeaviateKey(str, Enum):
    API_KEY = "api_key"
    URL = "url"
    MAX_SIMILARITY_DISTANCE = "max_similarity_distance"


class SchemaDiffState(str, Enum):
    IMMUTABLE = "immutable"
    REQUIRED = "required"
    DEFAULT = "default"
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class ProtectedSchemaNames(str, Enum):
    Documents = "Documents"
    DocumentsChunks = "DocumentsChunks"
    Messages = "Messages"
    Chats = "Chats"

    @staticmethod
    def to_list():
        return [
            ProtectedSchemaNames.Documents.value,
            ProtectedSchemaNames.DocumentsChunks.value,
            ProtectedSchemaNames.Messages.value,
            ProtectedSchemaNames.Chats.value,
        ]


class ProtectedPropertyNames(str, Enum):
    UniqueIdentifier = "unique_identifier"
    Content = "content"
    ContentHash = "content_hash"
    Chunks = "chunks"
    ItemId = "item_id"
    Document = "document"
    Index = "index"
    SourceDocuments = "source_documents"
    DerivedDocuments = "derived_documents"

    @staticmethod
    def to_list():
        return [
            ProtectedPropertyNames.UniqueIdentifier.value,
            ProtectedPropertyNames.Content.value,
            ProtectedPropertyNames.ContentHash.value,
            ProtectedPropertyNames.Chunks.value,
            ProtectedPropertyNames.ItemId.value,
            ProtectedPropertyNames.Document.value,
            ProtectedPropertyNames.Index.value,
            ProtectedPropertyNames.SourceDocuments.value,
            ProtectedPropertyNames.DerivedDocuments.value,
        ]


class Cases(str, Enum):
    upper = "upper"
    lower = "lower"

    @staticmethod
    def get(item: str):
        for case in Cases:
            if item == case.value:
                return case


class Patterns(str, Enum):
    pattern_star = "pattern*"
    star_pattern = "pattern*"
    star_pattern_star = "*pattern*"
    lower = "lower"

    @staticmethod
    def get(item: str):
        for pattern in Patterns:
            if item == pattern.value:
                return pattern


class SortOrder(str, Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"


class FilterOperator(str, Enum):
    EQUAL = "Equal"
    NOT_EQUAL = "NotEqual"
    GREATER_THAN = "GreaterThan"
    GREATER_THAN_EQUAL = "GreaterThanEqual"
    LESS_THAN = "LessThan"
    LESS_THAN_EQUAL = "LessThanEqual"
    LIKE = "Like"
    WITHIN_GEORANGE = "WithinGeoRange"
    IS_NULL = "IsNull"
    CONTAINS_ANY = "ContainsAny"  # Only for array and text properties
    CONTAINS_ALL = "ContainsAll"  # Only for array and text properties


class DataTypeInput(str, Enum):
    TEXT = "text"
    TEXT_ARRAY = "text_array"
    INT = "int"
    INT_ARRAY = "int_array"
    BOOL = "bool"
    BOOL_ARRAY = "bool_array"
    NUMBER = "number"
    NUMBER_ARRAY = "number_array"
    DATE = "date"
    DATE_ARRAY = "date_array"
    UUID = "uuid"
    UUID_ARRAY = "uuid_array"
    GEO_COORDINATES = "geoCoordinates"
    PHONE_NUMBER = "phoneNumber"


class ValueTypes(str, Enum):
    INT = "valueInt"
    BOOL = "valueBoolean"
    TEXT = "valueText"
    NUMBER = "valueNumber"
    DATE = "valueDate"
    GEO_COORDINATES = "valueGeoRange"


class ChangeEntityType(str, Enum):
    SCHEMA = "schema"
    PROPERTY = "property"
    FILTER = "filter"


class FileSystemType(str, Enum):
    FOLDER = "folder"
    FILE = "file"


class BaseFunctionNames(str, Enum):
    GET_MESSAGES = "vector_bridge__get_messages"
    GET_DOCUMENTS_DATA = "vector_bridge__get_documents_data"
    ADD_TO_CORE_KNOWLEDGE = "vector_bridge__add_to_core_knowledge"
    REMOVE_FROM_CORE_KNOWLEDGE = "vector_bridge__remove_from_core_knowledge"


class PropertyKey(str, Enum):
    DESCRIPTION = "property_description"
    SORTING_SUPPORTED = "sorting_supported"
    RETURNED = "returned"


class FilterKey(str, Enum):
    DESCRIPTION = "filter_description"
    FILTERING_SUPPORTED = "filtering_supported"
    FILTER_SETTINGS = "filter_settings"


class MessageStorageMode(str, Enum):
    VECTOR_DB = "VECTOR_DB"
    DB = "DB"


class IntegrationEndpointsAccessibility(str, Enum):
    OPEN = "OPEN"
    AUTH_PROTECTED = "AUTH_PROTECTED"


class LogsFilter(str, Enum):
    USER = "USER"
    API_KEY_HASH = "API_KEY_HASH"


class UsageFilter(str, Enum):
    ORGANIZATION = "ORGANIZATION"
    INTEGRATION = "INTEGRATION"
    API_KEY_HASH = "API_KEY_HASH"


class OpenAIModels(str, Enum):
    GPT_4_o_mini = "gpt-4o-mini"
    GPT_4_o = "gpt-4o"
    GPT_o_1 = "o1"
    GPT_o_1_mini = "o1-mini"
    GPT_o_3 = "o3"
    GPT_o_3_mini = "o3-mini"
    GPT_o_4_mini = "o4-mini"
    GPT_4_1_nano = "gpt-4.1-nano"
    GPT_4_1_mini = "gpt-4.1-mini"
    GPT_4_1 = "gpt-4.1"


class AnthropicModels(str, Enum):
    CLAUDE_V4_0_OPUS = "claude-opus-4-20250514"
    CLAUDE_V4_0_SONNET = "claude-sonnet-4-20250514"
    CLAUDE_V3_7_SONNET = "claude-3-7-sonnet-latest"
    CLAUDE_V3_5_SONNET = "claude-3-5-sonnet-latest"
    CLAUDE_V3_5_HAIKU = "claude-3-5-haiku-latest"


class DeepSeekModels(str, Enum):
    CHAT = "deepseek-chat"
    REASONER = "deepseek-reasoner"


class FileAccessType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"


class FileCheckStatus(str, Enum):
    FILE_NAME = "File with the same name"
    FILE_CONTENT = "File with the same content"
    PARENT_FOLDER = "Parent folder exists"
    SOURCE_DOCUMENTS = "Source documents exist"


class FileSystemError(str, Enum):
    FOLDER_CAN_NOT_BE_DOWNLOADED = "Folder can not be downloaded"
    FILE_IS_PRIVATE = "File is private"
    CAN_NOT_BE_PROCESSED = "You can not process this file"
    CAN_NOT_CHANGE_ACCESS_RIGHTS = "You can not change access rights"
    CAN_NOT_CHANGE_ACCESS_RIGHTS_OF_FILE_CREATOR = "You can not change access rights of a file creator"
    CLOUD_STORAGE_OR_VECTORIZATION_MUST_BE_SELECTED = "Either cloud storage or vectorization must be selected"
    DOWNLOAD_LINK_HAS_EXPIRED = "Download link has expired"
    INVALID_OBJECT_NAME_FORMAT = "Invalid object name format"
    FOLDER_ALREADY_EXISTS = "Folder with the same name is already created"
    FILE_NAME_CONFLICT = "File with the same name is already created"
    FILE_OR_FOLDER_NAME_CONFLICT = "File or Folder with the same name is already created"
    FILE_CONTENT_CONFLICT = "File with the same content is already created"
    PARENT_FOLDER_NOT_FOUND = "Parent folder does not exist"
    FILE_OR_FOLDER_NOT_FOUND = "Folder or file does not exist"
    FILE_OR_FOLDER_IS_PRIVATE = "Folder or file is private"
    TARGET_IS_PRIVATE = "Target folder or file is private"
    ONLY_EMPTY_FOLDER_DELETABLE = "Only an empty folder can be deleted"
    FOLDER_CANNOT_BE_MOVED = "Folder can not be moved"
    TARGET_FOLDER_NOT_FOUND = "The target folder does not exist"
    DELETION_FAILED = "Failed to delete a file or a folder"
    FILE_NOT_FOUND = "File not found"
    INVALID_PAYLOAD = "Invalid payload"
    INVALID_PAYLOAD_FORMAT = "Invalid payload format"
    UPLOAD_URL_HAS_EXPIRED = "Upload URL has expired"
    INVALID_EXPIRATION_FORMAT = "Invalid expiration format"
