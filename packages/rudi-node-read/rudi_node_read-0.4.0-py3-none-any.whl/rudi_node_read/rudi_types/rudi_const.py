from re import compile
from typing import Final, Literal, get_args

from rudi_node_read.utils.err import LiteralUnexpectedValueException

# -----[ RUDI version ]-------------------------------------------------------------------------------------------------

# RUDI version regular expression: "1.2.3beta" is OK
REGEX_RUDI_VERSION = compile(r"^[0-9]{1,2}\.[0-9]{1,2}(\.[0-9]{1,2})?[a-z]*$")

# -----[ RUDI objects ]-------------------------------------------------------------------------------------------------
RudiObjectTypeStr = Literal["resources", "organizations", "contacts", "media", "reports"]
RUDI_OBJECT_TYPES = get_args(RudiObjectTypeStr)


# -----[ Languages ]----------------------------------------------------------------------------------------------------
Language = Literal[
    "cs",
    "da",
    "de",
    "en",
    "el",
    "es",
    "fr",
    "hu",
    "it",
    "no",
    "pl",
    "pt",
    "ro",
    "ru",
    "sk",
]
RECOGNIZED_LANGUAGES = get_args(Language)

# -----[ Themes ]-------------------------------------------------------------------------------------------------------
Themes: Final = {
    "economy": {"fr": "Economie", "en": "Economy"},
    "citizenship": {"fr": "Citoyenneté", "en": "Citizenship"},
    "energyNetworks": {"fr": "Réseaux, Energie", "en": "Networks, Energy"},
    "culture": {"fr": "Culture, Sports, Loisirs", "en": "Culture, Sports, Leisure"},
    "transportation": {"fr": "Mobilité, Transport", "en": "Transportation"},
    "children": {"fr": "Enfance", "en": "Children"},
    "environment": {"fr": "Environnement", "en": "Environment"},
    "townPlanning": {"fr": "Urbanisme", "en": "Town planning"},
    "location": {"fr": "Référentiels géographiques", "en": "Location"},
    "education": {"fr": "Education", "en": "Eduction"},
    "publicSpace": {"fr": "Espace public", "en": "Public space"},
    "health": {"fr": "Santé, Sécurité", "en": "Health, security"},
    "housing": {"fr": "Logement", "en": "Housing"},
    "society": {"fr": "Social", "en": "Society"},
}
theme_translations = {}
for key in Themes:
    theme_translations[key] = key
    for lang in ["fr", "en"]:
        theme_translations[Themes[key][lang]] = key
ThemeTranslation: Final = theme_translations

# -----[ Licences ]-----------------------------------------------------------------------------------------------------
LicenceType = Literal["STANDARD", "CUSTOM"]
LICENCE_TYPES = get_args(LicenceType)
LICENCE_TYPE_STANDARD: Final[str] = "STANDARD"
LICENCE_TYPE_CUSTOM: Final[str] = "CUSTOM"

LicenceCode = Literal[
    "apache-2.0",
    "cc-by-nd-4.0",
    "etalab-1.0",
    "etalab-2.0",
    "gpl-3.0",
    "mit",
    "odbl-1.0",
    "public-domain-cc0",
]
LICENCE_CODES = get_args(LicenceCode)

# -----[ Media types ]--------------------------------------------------------------------------------------------------
MediaType = Literal["FILE", "SERVICE", "SERIES"]
MEDIA_TYPES = get_args(MediaType)
MEDIA_TYPE_FILE: Literal["FILE"] = "FILE"
MEDIA_TYPE_SERVICE: Literal["SERVICE"] = "SERVICE"
MEDIA_TYPE_SERIES: Literal["SERIES"] = "SERIES"

# -----[ Metadata general storage statuses ]----------------------------------------------------------------------------
StorageStatus = Literal["pending", "online", "archived", "unavailable"]
STORAGE_STATUSES = get_args(StorageStatus)

MetadataStatus = Literal["local", "incomplete", "refused", "sent", "published", "deleted", "unset"]
METADATA_STATUSES = get_args(MetadataStatus)

# -----[ File storage statuses ]----------------------------------------------------------------------------------------
FileStorageStatus = Literal["nonexistant", "available", "missing", "archived", "removed"]
FILE_STORAGE_STATUSES = get_args(FileStorageStatus)

# -----[ Hash algorithms ]----------------------------------------------------------------------------------------------
HashAlgorithm = Literal["MD5", "SHA-256", "SHA-512"]
HASH_ALGORITHMS = get_args(HashAlgorithm)

# -----[ File extensions & MIME types ]---------------------------------------------------------------------------------
FileExtensions: Final = {
    ".3gp": "video/3gpp",
    ".3gpp": "video/3gpp",
    ".7z": "application/x-7z-compressed",
    ".aac": "audio/aac",
    ".apng": "image/apng",
    ".avi": "video/x-msvideo",
    ".bin": "application/octet-stream",
    ".bmp": "image/bmp",
    ".bz": "application/x-bzip",
    ".bz2": "application/x-bzip2",
    ".css": "text/css",
    ".csv": "text/csv",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".epub": "application/epub+zip",
    ".exe": "application/x-executable",
    ".flif": "image/flif",
    ".geojson": "application/geo+json",
    ".gif": "image/gif",
    ".gz": "application/gzip",
    ".gzip": "application/gzip",
    ".htm": "text/html",
    ".html": "text/html",
    ".ico": "image/vnd.microsoft.icon",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".js": "application/javascript",
    ".json": "application/json",
    ".jsonld": "application/ld+json",
    ".m4a": "audio/m4a",
    ".mkv": "video/x-matroska",
    ".mng": "image/x-mng",
    ".mov": "video/quicktime",
    ".mp3": "audio/mpeg",
    ".mp4": "video/mp4",
    ".mpeg": "video/mpeg",
    ".mpg": "video/mpeg",
    ".odp": "application/vnd.oasis.opendocument.presentation",
    ".ods": "application/vnd.oasis.opendocument.spreadsheet",
    ".odt": "application/vnd.oasis.opendocument.text",
    ".oga": "audio/ogg",
    ".ogg": "audio/ogg",
    ".ogv": "video/ogg",
    ".otf": "font/otf",
    ".pdf": "application/pdf",
    ".php": "text/php",
    ".png": "image/png",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".py": "text/x-python",
    ".sql": "application/sql",
    ".tar": "application/x-tar",
    ".tar.bz": "application/x-bzip",
    ".tar.bz2": "application/x-bzip2",
    ".tar.gz": "application/gzip",
    ".tgz": "application/gzip",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".ttf": "font/ttf",
    ".txt": "text/plain",
    ".wav": "audio/wav",
    ".weba": "audio/webm",
    ".webm": "video/webm",
    ".webp": "image/webp",
    ".wmv": "video/x-ms-wmv",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xml": "text/xml",
    ".yaml": "text/x-yaml",
    ".yml": "text/x-yaml",
    ".zip": "application/zip",
    ".zst": "application/zstd",
}
FILE_EXTENSIONS = get_args(FileExtensions)

MimeTypes = Literal[
    "application/epub+zip",
    "application/geo+json",
    "application/graphql",
    "application/gzip",
    "application/javascript",
    "application/json",
    "application/ld+json",
    "application/msword",
    "application/octet-stream",
    "application/pdf",
    "application/sql",
    "application/vnd.api+json",
    "application/vnd.ms-excel",
    "application/vnd.ms-powerpoint",
    "application/vnd.oasis.opendocument.presentation",
    "application/vnd.oasis.opendocument.spreadsheet",
    "application/vnd.oasis.opendocument.text",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/x-7z-compressed",
    "application/x-bzip",
    "application/x-bzip2",
    "application/x-executable",
    "application/x-tar",
    "application/x-www-form-urlencoded",
    "application/xml",
    "application/zip",
    "application/zstd",
    "audio/aac",
    "audio/m4a",
    "audio/mpeg",
    "audio/ogg",
    "audio/wav",
    "audio/webm",
    "font/otf",
    "font/ttf",
    "image/apng",
    "image/bmp",
    "image/flif",
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/tiff",
    "image/vnd.microsoft.icon",
    "image/webp",
    "image/x-mng",
    "multipart/form-data",
    "text/css",
    "text/csv",
    "text/html",
    "text/markdown",
    "text/php",
    "text/plain",
    "text/x-markdown",
    "text/x-yaml",
    "text/xml",
    "video/3gpp",
    "video/mp4",
    "video/mpeg",
    "video/ogg",
    "video/quicktime",
    "video/webm",
    "video/x-matroska",
    "video/x-ms-wmv",
    "video/x-msvideo",
    "application/epub+zip+crypt",
    "application/geo+json+crypt",
    "application/graphql+crypt",
    "application/gzip+crypt",
    "application/javascript+crypt",
    "application/json+crypt",
    "application/ld+json+crypt",
    "application/msword+crypt",
    "application/octet-stream+crypt",
    "application/pdf+crypt",
    "application/sql+crypt",
    "application/vnd.api+json+crypt",
    "application/vnd.ms-excel+crypt",
    "application/vnd.ms-powerpoint+crypt",
    "application/vnd.oasis.opendocument.presentation+crypt",
    "application/vnd.oasis.opendocument.spreadsheet+crypt",
    "application/vnd.oasis.opendocument.text+crypt",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation+crypt",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet+crypt",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document+crypt",
    "application/x-7z-compressed+crypt",
    "application/x-bzip+crypt",
    "application/x-bzip2+crypt",
    "application/x-executable+crypt",
    "application/x-tar+crypt",
    "application/x-www-form-urlencoded+crypt",
    "application/xml+crypt",
    "application/zip+crypt",
    "application/zstd+crypt",
    "audio/aac+crypt",
    "audio/m4a+crypt",
    "audio/mpeg+crypt",
    "audio/ogg+crypt",
    "audio/wav+crypt",
    "audio/webm+crypt",
    "font/otf+crypt",
    "font/ttf+crypt",
    "image/apng+crypt",
    "image/bmp+crypt",
    "image/flif+crypt",
    "image/gif+crypt",
    "image/jpeg+crypt",
    "image/png+crypt",
    "image/tiff+crypt",
    "image/vnd.microsoft.icon+crypt",
    "image/webp+crypt",
    "image/x-mng+crypt",
    "multipart/form-data+crypt",
    "text/css+crypt",
    "text/csv+crypt",
    "text/html+crypt",
    "text/markdown+crypt",
    "text/php+crypt",
    "text/plain+crypt",
    "text/x-markdown+crypt",
    "text/x-yaml+crypt",
    "text/xml+crypt",
    "video/3gpp+crypt",
    "video/mp4+crypt",
    "video/mpeg+crypt",
    "video/ogg+crypt",
    "video/quicktime+crypt",
    "video/webm+crypt",
    "video/x-matroska+crypt",
    "video/x-ms-wmv+crypt",
    "video/x-msvideo+crypt",
]
MIME_TYPES = get_args(MimeTypes)

MimeTypesUtf8Text = Literal[
    "application/geo+json",
    "application/graphql",
    "application/javascript",
    "application/json",
    "application/ld+json",
    "application/x-yaml",
    "application/xml",
]
MIME_TYPES_UTF8_TEXT = get_args(MimeTypesUtf8Text)

ConnectorParameterTypes = Literal["STRING", "BOOLEAN", "DATE", "LONG", "DOUBLE", "ENUM"]
CONNECTOR_PARAMS_TYPES = get_args(ConnectorParameterTypes)


def check_is_literal(val, series: tuple, err_msg: str = "incorrect value"):
    """
    Check if input value is in the given series, raise an error with input message otherwise
    :param val: the value to check
    :param series: the series of accepted values
    :param err_msg: error message raised if the value was not found in the series
    :return: the checked value
    """
    if val not in series:
        raise LiteralUnexpectedValueException(val, series, err_msg)
    return val


def check_is_literal_or_none(val, series: tuple, err_msg: str = "incorrect value"):
    if val is None:
        return None
    return check_is_literal(val=val, series=series, err_msg=err_msg)


def check_rudi_version(version: str):
    if not (isinstance(version, str) and REGEX_RUDI_VERSION.match(version)):
        raise ValueError(f"Incorrect RUDI metadata version: '{version}'")
    return version
