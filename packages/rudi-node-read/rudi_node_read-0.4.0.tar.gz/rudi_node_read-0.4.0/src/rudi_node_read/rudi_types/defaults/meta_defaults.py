from typing import Final, Literal

from rudi_node_read.rudi_types.rudi_const import Language

# Default Language for the descriptions
DEFAULT_LANG: Language = "fr"

# Current version for RUDI Node metadata
RUDI_API_VERSION: Final[str] = "1.4.0"

# Current version for ODS
ODS_API_VERSION: str = "2.1"

# Default contact when none is provided in the source metadata
# Structure: https://app.swaggerhub.com/apis/OlivierMartineau/RUDI-PRODUCER/1.3.0#/Contact
DEFAULT_CONTACT: dict = {"contact_name": "Rudi node admin", "email": "community@rudi-univ-rennes1.fr"}

# Default producer when none is provided in the source metadata
# Structure: https://app.swaggerhub.com/apis/OlivierMartineau/RUDI-PRODUCER/1.3.0#/Organization
DEFAULT_PRODUCER: dict = {"organization_name": "Aucun Producteur"}

# Metadata publisher can differ from data producer.
# Select the value for the `metadata_info.publisher` field in RUDI metadata:
# - 'empty' if you want to let the field empty
# - 'producer' if the field should be filled with the data producer organization
# - 'default' if the field should be filled with the following default publisher
ENSURE_DEF_PUBLISHER: Literal["empty", "default", "producer"] = "default"

# Default organization when none is provided in the source metadata
# Structure: https://app.swaggerhub.com/apis/OlivierMartineau/RUDI-PRODUCER/1.3.0#/Organization
DEFAULT_PUBLISHER: dict = {
    "organization_name": "Univ. Rennes / IRISA",
    "organization_address": "263 avenue du Général Leclerc, 35 042 RENNES Cedex",
}

# Correspondences between ODS licences and RUDI standard licences
# Licences on an ODS server: https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets?limit=100&offset=0&group_by=default.license
# RUDI standard licence codes: https://bacasable.fenix.rudi-univ-rennes1.fr/api/admin/licence_codes
STD_LICENCES_CORRESPONDENCES: dict = {
    "odbl": "odbl-1.0",
    "licence ouverte.*1": "etalab-1.0",
    "licence ouverte": "etalab-2.0",
    "open license.*1": "etalab-1.0",
    "open license": "etalab-2.0",
    "CC BY-ND": "cc-by-nd-4.0",
    "geofla": "etalab-1.0",
    "www.insee.fr.*information": "public-domain-cc0",
}

# Default licence that will be associated to the data when no licence is found
DEFAULT_LICENCE: str = "odbl-1.0"
