from abc import ABC
from json import dumps

from deepdiff import DeepDiff

from rudi_node_read.rudi_types.rudi_const import (
    CONNECTOR_PARAMS_TYPES,
    FILE_STORAGE_STATUSES,
    HASH_ALGORITHMS,
    MEDIA_TYPE_FILE,
    MEDIA_TYPE_SERVICE,
    MIME_TYPES,
    FileStorageStatus,
    HashAlgorithm,
    MediaType,
    check_is_literal,
    check_is_literal_or_none,
)
from rudi_node_read.rudi_types.rudi_contact import uuid4_str
from rudi_node_read.rudi_types.rudi_dates import Date, RudiDates
from rudi_node_read.utils.log import log_d
from rudi_node_read.utils.serializable import Serializable
from rudi_node_read.utils.type_dict import check_has_key, check_is_dict
from rudi_node_read.utils.type_list import check_is_list_or_none
from rudi_node_read.utils.type_string import (
    check_is_string,
    check_is_string_or_none,
    check_is_uuid4,
)
from rudi_node_read.utils.typing_utils import (
    check_is_int,
    check_type,
    does_inherit_from,
    get_type_name,
)

NORMALIZED_CONNECTOR_PARAMS_TYPES = {
    "STR": "STRING",
    "BOOL": "BOOLEAN",
    "INT": "LONG",
    "FLOAT": "DOUBLE",
}


def normalize_connector_parameter_type(param_type: str, accept_none: bool = False):
    upper_param_type: str = check_is_string(param_type).upper()  # type: ignore
    if upper_param_type in CONNECTOR_PARAMS_TYPES:
        return upper_param_type
    normalized_type = NORMALIZED_CONNECTOR_PARAMS_TYPES.get(upper_param_type)
    if normalized_type is None and accept_none:
        return None
    return check_is_literal(param_type if normalized_type is None else normalized_type, CONNECTOR_PARAMS_TYPES)


def check_is_accepted_value(value, accepted_values: list | None = None):
    if (check_is_list_or_none(accepted_values) is not None) and (value not in accepted_values):
        raise ValueError(
            f"incoherence in connector parameter: input {value} is not in accepted values {accepted_values}"
        )
    return value


def get_normalized_type_name(value):
    if isinstance(value, str):
        if value.lower() in ("true", "false"):
            return "bool"
    return get_type_name(value)


def normalize_connector_values(value, value_type: str | None = None, accepted_values: list | None = None):
    if value_type is None:
        type_name = get_type_name(value)
        normalized_val_type = normalize_connector_parameter_type(type_name, accept_none=True)
        check_is_list_or_none(accepted_values)
        if normalized_val_type is None:
            # We'll need to cast the value into string for it to get accepted in RUDI
            end_accepted_values = [str(av) for av in accepted_values] if accepted_values is not None else None
            return [check_is_accepted_value(str(value), end_accepted_values), "STRING", end_accepted_values]
        else:
            return [check_is_accepted_value(value, accepted_values), normalized_val_type, accepted_values]
    else:
        # log_d(here, "in", value, f"({value_type})")
        normalized_val_type = normalize_connector_parameter_type(value_type)
        if normalize_connector_parameter_type(get_normalized_type_name(value)) != normalized_val_type:
            raise ValueError(f"incoherence in connector parameter type: input '{value}' is not of type '{value_type}'")
        return [check_is_accepted_value(value, accepted_values), normalized_val_type, accepted_values]


class RudiMediaConnectorParameter(Serializable):
    def __init__(
        self,
        key: str,
        value,
        value_type: str | None = None,
        accepted_values: list | None = None,
        usage: str | None = None,
    ):
        self.key = check_is_string(key)
        [self.value, self.value_type, self.accepted_values] = normalize_connector_values(
            value, value_type, accepted_values
        )
        self.usage = check_is_string_or_none(usage)

    def to_json(self, keep_nones: bool = False) -> dict:
        self_obj = {"key": self.key, "value": self.value, "type": self.value_type}
        if keep_nones or self.usage is not None:
            self_obj["usage"] = self.usage
        if keep_nones or self.accepted_values is not None:
            self_obj["accepted_values"] = self.accepted_values
        return self_obj

    @staticmethod
    def from_json(o: dict | list):
        if isinstance(o, dict):
            [value, value_type, accepted_values] = normalize_connector_values(
                check_has_key(o, "value"),
                check_is_string_or_none(o.get("type")),
                check_is_list_or_none(o.get("accepted_values")),  # type: ignore
            )
            return RudiMediaConnectorParameter(
                key=check_is_string(check_has_key(o, "key")),  # type: ignore
                value=value,
                value_type=value_type,
                accepted_values=accepted_values,
                usage=check_is_string_or_none(o.get("usage")),  # type: ignore
            )
        if isinstance(o, list):
            return RudiMediaConnectorParameterList.from_json(o)

        raise TypeError("RudiMediaConnectorParameter.from_json input should be a dict")


class RudiMediaConnectorParameterList(Serializable, list[RudiMediaConnectorParameter]):
    def __init__(self, list_entries: RudiMediaConnectorParameter | list[RudiMediaConnectorParameter]):
        super().__init__()
        if isinstance(list_entries, RudiMediaConnectorParameter):
            self.append(list_entries)
        elif isinstance(list_entries, list):
            for entry in list_entries:
                self.append(check_type(entry, RudiMediaConnectorParameter))
        else:
            raise TypeError(f"input parameter should be a list, got '{get_type_name(list_entries)}'")

    def to_json(self, keep_nones: bool = False) -> dict | list:
        return [entry.to_json(keep_nones) for entry in self]

    @staticmethod
    def from_json(o: list | dict):
        if isinstance(o, dict):
            return RudiMediaConnectorParameterList([RudiMediaConnectorParameter.from_json(o)])
        if isinstance(o, list):
            return RudiMediaConnectorParameterList([RudiMediaConnectorParameter.from_json(entry) for entry in o])
        raise TypeError("Property 'connector_parameters' should be a list")


class RudiMediaConnector(Serializable):
    def __init__(
        self,
        url: str,
        interface_contract: str | None = None,
        connector_parameters: (
            RudiMediaConnectorParameterList | list[RudiMediaConnectorParameter] | RudiMediaConnectorParameter | None
        ) = None,
    ):
        self.url = check_is_string(url)
        self.interface_contract = check_is_string_or_none(interface_contract)
        self.connector_parameters = None
        if connector_parameters is not None:
            if isinstance(connector_parameters, RudiMediaConnectorParameterList):
                self.connector_parameters = connector_parameters
            elif isinstance(connector_parameters, list) or isinstance(
                connector_parameters, RudiMediaConnectorParameter
            ):
                self.connector_parameters = RudiMediaConnectorParameterList(connector_parameters)
            else:
                check_type(connector_parameters, RudiMediaConnectorParameterList)

    def to_json(self, keep_nones: bool = False) -> dict:
        self_json = {
            "url": self.url,
        }
        if self.interface_contract is not None:
            self_json["interface_contract"]: str = check_is_string(self.interface_contract)  # type: ignore
        if does_inherit_from(self.connector_parameters, list):
            self_json["connector_parameters"]: list = [  # type: ignore
                (connector_parameter.to_json(keep_nones)) for connector_parameter in self.connector_parameters  # type: ignore
            ]
        return self_json

    @staticmethod
    def from_json(o: dict):
        params_list = o.get("connector_parameters")
        connector_parameters = None if params_list is None else RudiMediaConnectorParameterList.from_json(params_list)

        return RudiMediaConnector(
            url=check_is_string(check_has_key(o, "url")),
            interface_contract=check_is_string_or_none(o.get("interface_contract")),
            connector_parameters=connector_parameters,
        )


class RudiChecksum(Serializable):
    def __init__(self, algo: HashAlgorithm, hash_str: str):
        self.algo = check_is_literal(algo, HASH_ALGORITHMS, "the value was not recognized as a hash algorithm ")
        self.hash_str = check_is_string(hash_str)

    def to_json(self, keep_nones: bool = False) -> dict:
        # log_d("RudiChecksum.to_json")
        return {"algo": self.algo, "hash": self.hash_str}

    def to_json_str(self, keep_nones: bool = False, ensure_ascii: bool = False, sort_keys: bool = False) -> str:
        return dumps(self.to_json(keep_nones=keep_nones), ensure_ascii=ensure_ascii, sort_keys=sort_keys)

    @staticmethod
    def from_json(o: dict):
        check_is_dict(o)
        algo: HashAlgorithm = check_is_literal(
            check_has_key(o, "algo"),
            HASH_ALGORITHMS,
            "the value was not recognized as a hash algorithm ",
        )  # type: ignore
        hash_str: str = check_is_string(check_has_key(o, "hash"))  # type: ignore
        return RudiChecksum(algo=algo, hash_str=hash_str)


class RudiMedia(Serializable, ABC):
    def __init__(
        self,
        media_id: str,
        media_type: MediaType,
        media_name: str,
        connector: RudiMediaConnector,
        media_caption: str | None = None,
        media_dates: RudiDates | None = None,
        collection_tag: str | None = None,
    ) -> None:
        super().__init__()
        self.media_id = check_is_uuid4(media_id)
        self.media_type = media_type
        self.media_name = check_is_string(media_name)
        self.connector: RudiMediaConnector = check_type(connector, RudiMediaConnector)  # type: ignore
        self.media_dates: RudiDates = check_type(media_dates, RudiDates) if media_dates else RudiDates()  # type: ignore

        # Media optional attributes
        self.media_caption = check_is_string_or_none(media_caption)
        self.collection_tag = check_is_string_or_none(collection_tag)

    @property
    def source_url(self):
        return self.connector.url

    @staticmethod
    def from_json(o: dict):
        check_is_dict(o)
        media_type = check_has_key(o, "media_type")
        if media_type == MEDIA_TYPE_FILE:
            return RudiMediaFile.from_json(o)
        if media_type == MEDIA_TYPE_SERVICE:
            return RudiMediaService.from_json(o)
        raise NotImplementedError(f"cannot create a media for type '{media_type}'")

    def to_json_str(self, keep_nones: bool = False, ensure_ascii: bool = False, sort_keys: bool = False) -> str:
        return dumps(self.to_json(keep_nones), ensure_ascii=ensure_ascii, sort_keys=sort_keys)


class RudiMediaService(RudiMedia):
    def __init__(
        self,
        media_id: str,
        media_name: str,
        connector: RudiMediaConnector,
        media_caption: str | None = None,
        media_dates: RudiDates | None = None,
        api_documentation_url: str | None = None,
        collection_tag: str | None = None,
    ):
        super().__init__(
            media_id=media_id,
            media_type=MEDIA_TYPE_SERVICE,
            media_name=media_name,
            connector=connector,
            media_caption=media_caption,
            media_dates=media_dates,
            collection_tag=collection_tag,
        )

        if connector.interface_contract is None:
            self.connector.interface_contract = "external"

        self.api_documentation_url = check_is_string_or_none(api_documentation_url)
        self.collection_tag = check_is_string_or_none(collection_tag)

    def to_json(self, keep_nones: bool = False) -> dict:
        out_obj = {
            "media_type": MEDIA_TYPE_SERVICE,
            "media_id": self.media_id,
            "media_name": self.media_name,
            "media_dates": self.media_dates.to_json(),
            "connector": self.connector.to_json(),
        }
        if keep_nones or self.media_caption:
            out_obj["media_caption"] = self.media_caption
        if keep_nones or self.api_documentation_url:
            out_obj["api_documentation_url"] = self.api_documentation_url
        return out_obj

    @staticmethod
    def from_json(o: dict):
        check_is_dict(o)
        media_type = check_has_key(o, "media_type")
        if media_type != MEDIA_TYPE_SERVICE:
            raise ValueError(f"This cannot be structured as a RudiMediaService: got 'media_type' = '{media_type}'")

        connector = RudiMediaConnector.from_json(check_has_key(o, "connector"))

        media_dates = RudiDates.from_json(o.get("media_dates"))

        return RudiMediaService(
            media_id=check_is_uuid4(check_has_key(o, "media_id")),
            media_name=check_has_key(o, "media_name"),
            connector=connector,
            media_caption=o.get("media_caption"),
            media_dates=media_dates,
            api_documentation_url=o.get("api_documentation_url"),
            collection_tag=o.get("collection_tag"),
        )


class RudiMediaFile(RudiMedia):
    def __init__(
        self,
        media_id: str,
        media_name: str,
        connector: RudiMediaConnector,
        file_type: str,  # MIME type
        file_size: int,
        checksum: RudiChecksum,
        media_caption: str | None = None,
        media_dates: RudiDates | None = None,
        file_encoding: str | None = None,
        file_structure: str | None = None,
        file_storage_status: FileStorageStatus | None = "missing",
        file_status_update: str | Date | None = Date.now_iso(),
        collection_tag: str | None = None,
    ):
        super().__init__(
            media_id=media_id,
            media_type=MEDIA_TYPE_FILE,  # type: ignore
            media_name=media_name,
            connector=connector,
            media_caption=media_caption,
            media_dates=media_dates,
            collection_tag=collection_tag,
        )
        # Media mandatory attributes
        if connector.interface_contract is None:
            self.connector.interface_contract = "dwnl"

        # MediaFile mandatory attributes
        self.file_type = check_is_literal(file_type, MIME_TYPES, "incorrect parameter for MIME type")
        self.file_size = check_is_int(file_size)
        self.checksum = check_type(checksum, RudiChecksum)

        # MediaFile optional attributes
        self.file_encoding = check_is_string_or_none(file_encoding)
        self.file_structure = check_is_string_or_none(file_structure)

        self.file_storage_status = check_is_literal_or_none(
            val=file_storage_status,
            series=FILE_STORAGE_STATUSES,
            err_msg="incorrect value for a file storage status",
        )
        self.file_status_update = (
            file_status_update
            if isinstance(file_status_update, Date)
            else Date.from_str(file_status_update, is_none_accepted=True)
        )

    @staticmethod
    def from_json(o: dict):
        check_is_dict(o)

        # Media mandatory attributes
        media_type = check_has_key(o, "media_type")
        if media_type != MEDIA_TYPE_FILE:
            raise ValueError(f"This cannot be structured as a RudiMediaFile: got 'media_type' = '{media_type}'")

        # MediaFile mandatory attributes
        file_type = check_is_literal(check_has_key(o, "file_type"), MIME_TYPES, "incorrect parameter for MIME type")

        # MediaFile optional attributes
        file_storage_status = o.get("file_storage_status")
        check_is_literal_or_none(
            file_storage_status,
            FILE_STORAGE_STATUSES,
            "value not accepted as a file storage status",
        )

        # log_d('RudiMediaFile.from_dict', 'preliminary checks OK')
        return RudiMediaFile(
            media_id=check_is_uuid4(check_has_key(o, "media_id")),
            media_name=check_is_string(check_has_key(o, "media_name")),
            connector=RudiMediaConnector.from_json(check_has_key(o, "connector")),
            file_type=file_type,
            file_size=check_is_int(check_has_key(o, "file_size")),
            checksum=RudiChecksum.from_json(check_has_key(o, "checksum")),
            media_caption=o.get("media_caption"),
            media_dates=RudiDates.from_json(o.get("media_dates")),
            file_encoding=o.get("file_encoding"),
            file_structure=o.get("file_structure"),
            file_storage_status=file_storage_status,
            file_status_update=Date.from_str(o.get("file_status_update")),
            collection_tag=o.get("collection_tag"),
        )

    def set_url(self, file_url: str):
        self.connector.url = file_url

    def set_status(self, storage_status: FileStorageStatus):
        self.file_storage_status = storage_status
        self.file_status_update = Date.now_iso_str()

    @staticmethod
    def from_local_file(file_local_path: str, media_id: str | None = uuid4_str(), file_url: str = "to_be_provided"):
        here = f"{RudiMediaFile}.from_local_file"
        file_info = FileDetails(file_local_path)
        log_d(here, "file_info", file_info)
        return RudiMediaFile(
            media_id=check_is_uuid4(media_id),
            media_name=file_info.name,
            connector=RudiMediaConnector(url=file_url, interface_contract="dwnl"),
            file_type=file_info.mime,
            file_size=file_info.size,
            checksum=RudiChecksum(algo="MD5", hash_str=file_info.md5),
        )


if __name__ == "__main__":  # pragma: no cover
    tests = "RudiMedia tests"
    rudi_file_json = {
        "checksum": {
            "algo": "SHA-256",
            "hash": "f72d0035896447b55ff27998d6fd8773a68b2770027336c09da2bc6fd67e2dcf",
        },
        "media_dates": {
            "created": "2022-01-21T10:40:28.781+00:00",
            "updated": "2022-01-21T10:40:28.781+00:00",
        },
        "connector": {
            "url": "https://bacasable.fenix.rudi-univ-rennes1.fr/storage/download/2611547a-42f1-4d7c-b736-2fef5cca30fe",
            "interface_contract": "dwnl",
            "connector_parameters": [
                {
                    "key": "random key 1",
                    "value": "random val 1",
                    "type": "STRING",
                    "usage": "test 1",
                    "accepted_values": ["random val 1", "random val 2"],
                }
            ],
        },
        "file_type": "image/png",
        "file_size": 414931,
        "file_storage_status": "available",
        "file_status_update": "2023-04-14T13:57:15.859+00:00",
        "media_id": "2611547a-42f1-4d7c-b736-2fef5cca30fe",
        "media_type": "FILE",
        "media_name": "unicorn.png",
    }
    # log_d(tests, "RudiMediaFile.from_json")
    log_d(tests, "RudiMediaFile.from_json", rudi_file := RudiMediaFile.from_json(rudi_file_json))

    # log_d(tests, "RudiMediaFile.to_json")
    log_d(tests, "RudiMediaFile.to_json", rudi_file.to_json())

    rudi_service_json = {
        "connector": {
            "url": "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/qualite-de-service-selon-operateurs-et-axe-de-transport-2g-3g-4g/exports",
            "interface_contract": "external",
            "connector_parameters": [
                {
                    "key": "random key 2",
                    "value": "random val 2",
                    "type": "string",
                    "usage": "test 2",
                    "accepted_values": ["random val 1", "random val 2"],
                }
            ],
        },
        "media_id": "e611547a-42f1-4d7c-b736-2fef5cca30fe",
        "media_type": "SERVICE",
        "media_name": "exports disponibles",
    }
    log_d(tests, "RudiMediaService.from_json", rudi_service := RudiMediaService.from_json(rudi_service_json))
    log_d(tests, "RudiMediaService.to_json", rudi_service.to_json())
    log_d(tests, "RudiMediaService.to_json diff", DeepDiff(rudi_service_json, rudi_service.to_json()))

    params = RudiMediaConnectorParameter(key="key1", value=3)
    log_d(tests, "RudiMediaConnectorParameters", params.to_json())
    log_d(
        tests,
        "RudiMediaConnector",
        RudiMediaConnector(
            url="https://app.swaggerhub.com/apis/OlivierMartineau/RUDI-PRODUCER/1.3.0#/MediaFile",
            connector_parameters=params,
        ).to_json(),
    )

    connect_params = RudiMediaConnectorParameter.from_json(
        {
            "key": "random key 3",
            "value": "random val 3",
            "type": "string",
            "usage": "test 3",
            "accepted_values": ["random val 1", "random val 2", "random val 3"],
        }
    )
    log_d(tests, "connect_params", connect_params)

    connect_params = RudiMediaConnectorParameter.from_json(
        {
            "key": "random key",
            "value": {"e": "value is a dict and will be stringified"},
            "usage": "test",
            "accepted_values": [{"e": "value is a dict and will be stringified"}],
        }
    )
    log_d(tests, "connect_params", connect_params)

    connect_params = RudiMediaConnectorParameter.from_json(
        {
            "key": "random key",
            "value": {"e": "value is a dict and will be stringified"},
            # "type": "dict",
            "usage": "test",
            "accepted_values": [{"e": "value is a dict and will be stringified"}],
        }
    )
    log_d(tests, "connect_params", connect_params)

    log_d(tests, "rudi_file.to_json_str()", rudi_file.to_json_str(sort_keys=True))
    log_d(tests, "dumps(rudi_file_json)", dumps(rudi_file_json, sort_keys=True))
