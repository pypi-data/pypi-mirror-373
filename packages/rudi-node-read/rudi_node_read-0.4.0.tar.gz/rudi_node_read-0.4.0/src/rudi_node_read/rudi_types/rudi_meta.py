from uuid import UUID

from rudi_node_read.rudi_types.defaults.meta_defaults import RUDI_API_VERSION
from rudi_node_read.rudi_types.rudi_const import (
    METADATA_STATUSES,
    RECOGNIZED_LANGUAGES,
    STORAGE_STATUSES,
    Language,
    StorageStatus,
    ThemeTranslation,
    check_is_literal,
    check_is_literal_or_none,
)
from rudi_node_read.rudi_types.rudi_contact import RudiContact
from rudi_node_read.rudi_types.rudi_dates import Date, RudiDates
from rudi_node_read.rudi_types.rudi_dictionary_entry import RudiDictionaryEntryList
from rudi_node_read.rudi_types.rudi_geo import RudiGeography
from rudi_node_read.rudi_types.rudi_licence import RudiAccessCondition, RudiLicence
from rudi_node_read.rudi_types.rudi_media import (
    RudiMedia,
    RudiMediaFile,
    RudiMediaService,
)
from rudi_node_read.rudi_types.rudi_meta_misc import (
    RudiDatasetSize,
    RudiDataTemporalSpread,
    RudiMetadataInfo,
)
from rudi_node_read.rudi_types.rudi_org import RudiOrganization
from rudi_node_read.utils.log import log_d
from rudi_node_read.utils.serializable import Serializable
from rudi_node_read.utils.type_dict import check_has_key, check_is_dict
from rudi_node_read.utils.type_list import ensure_is_str_list
from rudi_node_read.utils.type_string import (
    check_is_string,
    check_is_string_or_none,
    check_is_uuid4,
    uuid4_str,
)
from rudi_node_read.utils.typing_utils import (
    check_type,
    check_type_or_null,
    get_type_name,
)


def normalize_theme(theme: str | list) -> str:
    normalized_theme = ThemeTranslation.get(theme[0] if isinstance(theme, list) else theme)
    return (
        normalized_theme.strip()
        if normalized_theme is not None
        else (theme[0] if isinstance(theme, list) else theme).strip()
    )
    # TODO what if theme is not in ThemeTranslation ?


class RudiMetadata(Serializable):
    def __init__(
        self,
        global_id: str | UUID,
        resource_title: str,
        synopsis: RudiDictionaryEntryList,
        summary: RudiDictionaryEntryList,
        theme: str,
        keywords: list[str],
        producer: RudiOrganization,
        contacts: list[RudiContact],
        available_formats: list[RudiMedia],
        dataset_dates: RudiDates,
        storage_status: StorageStatus,
        metadata_info: RudiMetadataInfo,
        local_id: str | None = None,
        doi: str | None = None,
        resource_languages: list[Language] | Language | None = None,
        temporal_spread: RudiDataTemporalSpread | None = None,
        dataset_size: RudiDatasetSize | None = None,
        geography: RudiGeography | None = None,
        access_condition: RudiAccessCondition | None = None,
        metadata_source: str | None = None,
        collection_tag: str | None = None,
        metadata_status: str | None = None,
    ):
        """
        The RUDI metadata gathers the information about the files that are referenced in the RUDI node. They make it
        possible to search these. For this purpose, a number of inforamtion are required.
        See https://app.swaggerhub.com/apis/OlivierMartineau/RUDI-PRODUCER for the OpenAPI documentation.
        """
        # ---------- Mandatory parameters ----------
        self.global_id = check_is_uuid4(global_id)

        self.resource_title = check_is_string(resource_title)

        self.synopsis: RudiDictionaryEntryList = check_type(synopsis, RudiDictionaryEntryList)  # type:ignore
        self.summary: RudiDictionaryEntryList = check_type(summary, RudiDictionaryEntryList)
        # TODO clean summary

        self.theme = normalize_theme(theme)

        self.keywords = ensure_is_str_list(keywords)

        self.producer: RudiOrganization = check_type(producer, RudiOrganization)
        self.contacts: list[RudiContact] = [check_type(contact, RudiContact) for contact in contacts]

        self.available_formats: list[RudiMedia] = [
            check_type(media, (RudiMediaFile, RudiMediaService)) for media in available_formats
        ]
        self.dataset_dates: RudiDates = check_type(dataset_dates, RudiDates)
        self.storage_status: StorageStatus = check_is_literal(storage_status, STORAGE_STATUSES)

        self.access_condition = check_type(access_condition, RudiAccessCondition)
        self.metadata_info: RudiMetadataInfo = check_type(metadata_info, RudiMetadataInfo)

        # ---------- Optional parameters ----------
        self.local_id = check_is_string_or_none(local_id)
        self.doi = check_is_string_or_none(doi)

        self.resource_languages = (
            None
            if resource_languages is None
            else (
                [check_is_literal(resource_languages, RECOGNIZED_LANGUAGES)]
                if isinstance(resource_languages, str)
                else [check_is_literal(lang, RECOGNIZED_LANGUAGES) for lang in resource_languages]
            )
        )

        self.temporal_spread = check_type_or_null(temporal_spread, RudiDataTemporalSpread)
        self.geography = check_type_or_null(geography, RudiGeography)
        self.dataset_size = check_type_or_null(dataset_size, RudiDatasetSize)

        self.collection_tag = check_is_string_or_none(collection_tag)
        self.metadata_source = check_is_string_or_none(metadata_source)
        self.metadata_status = check_is_literal_or_none(metadata_status, METADATA_STATUSES)

    @staticmethod
    def from_json(o: dict):
        check_is_dict(o)

        # Mandatory attributes
        global_id = check_is_uuid4(check_has_key(o, "global_id"))
        resource_title = check_is_string(check_has_key(o, "resource_title"))

        synopsis: RudiDictionaryEntryList = RudiDictionaryEntryList.from_json(check_has_key(o, "synopsis"))  # type: ignore
        summary: RudiDictionaryEntryList = RudiDictionaryEntryList.from_json(check_has_key(o, "summary"))  # type: ignore

        theme: str = check_is_string(check_has_key(o, "theme"))
        keywords: list[str] = ensure_is_str_list(check_has_key(o, "keywords"))

        producer: RudiOrganization = RudiOrganization.from_json(check_has_key(o, "producer"))
        contact_list = check_has_key(o, "contacts")
        if isinstance(contact_list, list):
            contacts = [RudiContact.from_json(contact) for contact in contact_list]
        elif isinstance(contact_list, dict):
            contacts = [RudiContact.from_json(contact_list)]
        else:
            raise TypeError(
                f"incorrect type for contacts attribute, expected 'list', got '{get_type_name(contact_list)}'"
            )

        available_formats: list[RudiMedia] = [
            RudiMedia.from_json(media) for media in check_has_key(o, "available_formats")
        ]
        dataset_dates = RudiDates.from_json(check_has_key(o, "dataset_dates"))
        storage_status = check_is_literal(check_has_key(o, "storage_status"), STORAGE_STATUSES)
        access_condition = RudiAccessCondition.from_json(check_has_key(o, "access_condition"))

        metadata_info = RudiMetadataInfo.from_json(check_has_key(o, "metadata_info"))

        # ---------- Optional parameters ----------
        local_id = o.get("local_id")
        doi = o.get("doi")
        languages = o.get("resource_languages")
        resource_languages = (
            None if not languages else [check_is_literal(lang, RECOGNIZED_LANGUAGES) for lang in languages]
        )

        temporal_spread = RudiDataTemporalSpread.from_json(o.get("temporal_spread"))
        dataset_size = RudiDatasetSize.from_json(o.get("dataset_size"))
        geography = RudiGeography.from_json(o.get("geography"))
        collection_tag = check_is_string_or_none(o.get("collection_tag"))

        metadata_status = check_is_literal_or_none(o.get("metadata_status"), METADATA_STATUSES)

        return RudiMetadata(
            global_id=global_id,
            resource_title=resource_title,
            synopsis=synopsis,
            summary=summary,
            theme=theme,
            keywords=keywords,
            producer=producer,
            contacts=contacts,
            available_formats=available_formats,
            dataset_dates=dataset_dates,
            storage_status=storage_status,
            access_condition=access_condition,
            metadata_info=metadata_info,
            local_id=local_id,
            doi=doi,
            resource_languages=resource_languages,
            temporal_spread=temporal_spread,
            dataset_size=dataset_size,
            geography=geography,
            collection_tag=collection_tag,
            metadata_status=metadata_status,
        )

    def get_number_of_records(self) -> int | None:
        return self.dataset_size.number_of_records if self.dataset_size is not None else None

    def get_licence(self) -> RudiLicence:
        return self.access_condition.licence


if __name__ == "__main__":  # pragma: no cover
    tests = "RudiMetadataInfo tests"
    my_org = RudiOrganization(
        organization_id=uuid4_str(),
        organization_name="IRISA",
        organization_address="263 avenue du Général Leclerc, 35000 RENNES",
    )
    my_contact = RudiContact(
        contact_id=uuid4_str(),
        contact_name="Jean-Patrick Contactest",
        email="jean-patrick@contact.test",
        contact_summary="I ♥ oranges",
    )
    # log_d(tests, 'my_contact', my_contact)
    meta_info_json = {
        "api_version": RUDI_API_VERSION,
        "metadata_dates": {
            "created": "2023-05-12T16:40:39+02:00",
            "updated": "2023-05-12T16:40:39+02:00",
        },
        "metadata_contacts": [
            {
                "contact_id": "fc6975e8-4fa8-4b20-895a-b9a585498c45",
                "contact_name": "Jean-Patrick Contactest",
                "email": "jean-patrick@contact.test",
                "contact_summary": "I ♥ oranges",
            }
        ],
        "metadata_provider": {
            "organization_id": "c99d6875-f2e5-4fca-af9c-68b7314be905",
            "organization_name": "IRISA",
            "organization_address": "263 avenue du Général Leclerc, 35000 RENNES",
        },
    }
    log_d(tests, "meta_info_json", meta_info_json)
    log_d(tests, "info_json", RudiMetadataInfo.from_json(meta_info_json))
    meta_info = RudiMetadataInfo(
        RUDI_API_VERSION,
        RudiDates(),
        metadata_provider=my_org,
        metadata_contacts=[my_contact],
    )
    log_d(tests, "meta_info", meta_info)

    tests = "RudiMetadata tests"
    meta = {
        "temporal_spread": {"start_date": "2022-11-07T06:55:11.000Z"},
        "geography": {
            "bounding_box": {
                "west_longitude": -1.677803,
                "east_longitude": 1.677803,
                "south_latitude": -48.112834,
                "north_latitude": 48.112834,
            },
            "geographic_distribution": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-1.677803, -48.112834],
                        [1.677803, -48.112834],
                        [1.677803, 48.112834],
                        [-1.677803, 48.112834],
                        [-1.677803, -48.112834],
                    ]
                ],
                "bbox": [-1.677803, -48.112834, 1.677803, 48.112834],
            },
            "projection": "WGS 84 (EPSG:4326)",
        },
        "dataset_dates": {
            "created": "2023-04-12T02:00:38.000Z",
            "published": "2023-04-12T09:39:28.562Z",
            "updated": "2023-04-12T02:00:38.000Z",
        },
        "access_condition": {
            "licence": {"licence_type": "STANDARD", "licence_label": "etalab-1.0"},
            "confidentiality": {"restricted_access": False, "gdpr_sensitive": False},
        },
        "metadata_info": {
            "api_version": "1.3.2",
            "metadata_provider": {
                "organization_id": "44f5ac9d-34d6-44d0-99a9-0496654bde5c",
                "organization_name": "Breitenberg - Legros",
                "organization_address": "425 Hickle Crest, Duluth",
                "collection_tag": "rudi-test",
            },
            "metadata_contacts": [
                {
                    "contact_id": "f275bed9-6b62-43f1-b617-a392896a617c",
                    "contact_name": "Sherri Dickinson",
                    "email": "sherri.dickinson@irisa.fr",
                    "collection_tag": "rudi-test",
                }
            ],
            "metadata_dates": {
                "created": "2023-04-12T09:39:28.666Z",
                "updated": "2023-04-12T09:39:28.696Z",
            },
        },
        "global_id": "e8b513a1-8d0e-4824-9a7d-1087fc66af9d",
        "resource_title": "Synergistic system-worthy encoding",
        "synopsis": [{"lang": "fr", "text": "Tasty incentivize bricks-and-clicks systems"}],
        "summary": [
            {
                "lang": "fr",
                "text": "I'll index the wireless GB hard drive, that should capacitor the JSON firewall! You "
                "can't index the interface without programming the neural RSS application! Aliquid quasi "
                "earum. Debitis possimus sit aut voluptatum ut nostrum. At corrupti optio pariatur corrupti "
                "autem ut.",
            }
        ],
        "purpose": [{"lang": "fr", "text": "rudi-test"}],
        "theme": "education",
        "keywords": ["Compte administratif", "Santé"],
        "collection_tag": "rudi-test",
        "producer": {
            "organization_id": "fa557d8b-0892-47aa-809b-6da59081e0aa",
            "organization_name": "Gusikowski LLC",
            "organization_address": "4974 Altenwerth Wells, Brownville",
            "collection_tag": "rudi-test",
        },
        "contacts": [
            {
                "contact_id": "f275bed9-6b62-43f1-b617-a392896a617c",
                "contact_name": "Sherri Dickinson",
                "email": "sherri.dickinson@irisa.fr",
                "collection_tag": "rudi-test",
            },
            {
                "contact_id": "6371498a-f9df-46a5-b4e6-9dec377ada2b",
                "contact_name": "Wanda Torphy",
                "email": "wanda.torphy@irisa.fr",
                "collection_tag": "rudi-test",
            },
        ],
        "available_formats": [
            {
                "checksum": {"algo": "MD5", "hash": "4c9ee0f14e835927a1bbafde0eb89fb3"},
                "media_dates": {
                    "created": "2023-03-03T11:15:57.226Z",
                    "updated": "2023-03-03T11:15:57.226Z",
                },
                "connector": {
                    "url": "https://shared-rudi.aqmo.org/media/9de29661-a53a-4eea-835c-b0799e181636",
                    "interface_contract": "dwnl",
                },
                "file_type": "application/json",
                "file_size": 59016,
                "file_storage_status": "missing",
                "file_status_update": "2023-03-03T11:15:57.232Z",
                "media_id": "9de29661-a53a-4eea-835c-b0799e181636",
                "media_type": "FILE",
                "media_name": "Synergistic system-worthy encoding.json",
                "collection_tag": "rudi-test",
            }
        ],
        "resource_languages": ["fr"],
        "storage_status": "pending",
    }
    log_d(tests, "RudiMetadata.deserialize", rudi_meta := RudiMetadata.from_json(meta))
    rudi_meta2 = RudiMetadata.from_json(meta)
    log_d(tests, "RudiMetadata.__eq__", rudi_meta == rudi_meta2)
    rudi_meta2.metadata_info.metadata_dates.validated = Date.now_iso()
    log_d(tests, "RudiMetadata.__eq__", rudi_meta != rudi_meta2)
    log_d(tests, "RudiMetadata.to_json", rudi_meta2.to_json())
