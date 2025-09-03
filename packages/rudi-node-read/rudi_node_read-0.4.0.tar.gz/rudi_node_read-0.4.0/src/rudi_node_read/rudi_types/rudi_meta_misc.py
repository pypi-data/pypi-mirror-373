from rudi_node_read.rudi_types.defaults.meta_defaults import RUDI_API_VERSION
from rudi_node_read.rudi_types.rudi_const import check_rudi_version
from rudi_node_read.rudi_types.rudi_contact import RudiContact
from rudi_node_read.rudi_types.rudi_dates import Date, RudiDates
from rudi_node_read.rudi_types.rudi_org import RudiOrganization
from rudi_node_read.utils.log import log_d
from rudi_node_read.utils.serializable import Serializable
from rudi_node_read.utils.type_dict import check_has_key, check_is_dict
from rudi_node_read.utils.typing_utils import check_is_int_or_none, get_type_name


class RudiDatasetSize(Serializable):
    def __init__(self, number_of_records: int | None = None, number_of_fields: int | None = None):
        self.number_of_records = check_is_int_or_none(number_of_records, accept_castable=True)
        self.number_of_fields = check_is_int_or_none(number_of_fields, accept_castable=True)

    @staticmethod
    def from_json(o: dict | None):
        if o is None:
            return None
        check_is_dict(o)
        number_of_records = n if (n := o.get("number_of_records")) is not None else o.get("numbers_of_records")
        return RudiDatasetSize(number_of_records, o.get("number_of_fields"))


class RudiDataTemporalSpread(Serializable):
    def __init__(self, start_date: str, end_date: str | None = None):
        if start_date is None:
            raise ValueError("Input argument 'start_date' should not be null")
        self.start_date: Date = Date.from_json(start_date)  # type: ignore

        if end_date is None:
            self.end_date = None
        else:
            self.end_date = Date.from_json(end_date)
            if self.start_date > self.end_date:  # type: ignore
                raise ValueError(
                    f"Temporal spread implies start date is older than end date, got '{start_date}' > '{end_date}'"
                )

    @staticmethod
    def from_json(o: dict | None):
        if o is None:
            return None
        check_is_dict(o)
        return RudiDataTemporalSpread(check_has_key(o, "start_date"), o.get("end_date"))


class RudiMetadataInfo(Serializable):
    def __init__(
        self,
        api_version: str = RUDI_API_VERSION,
        metadata_dates: RudiDates | None = None,
        metadata_provider: RudiOrganization | None = None,
        metadata_contacts: list[RudiContact] | None = None,
        metadata_source: str | None = None,
    ):
        self.api_version = check_rudi_version(api_version)
        self.metadata_dates = metadata_dates if metadata_dates else RudiDates()
        self.metadata_provider = metadata_provider
        self.metadata_contacts = metadata_contacts
        self.metadata_source = metadata_source

    @staticmethod
    def from_json(o: dict):
        check_is_dict(o)
        provider = o.get("metadata_provider")
        metadata_provider = RudiOrganization.from_json(provider) if provider else None
        contacts = o.get("metadata_contacts")
        # log_d('RudiMetadataInfo.from_dict', 'metadata_contacts', contacts)
        if contacts is None:
            metadata_contacts = None
        elif isinstance(contacts, dict):
            metadata_contacts = [RudiContact.from_json(contacts)]
        elif isinstance(contacts, list):
            metadata_contacts = [RudiContact.from_json(contact) for contact in contacts]
        else:
            raise TypeError(
                f"incorrect object type for 'metadata_contacts'. Expected 'list[dict]', "
                f"got '{get_type_name(contacts)}'"
            )

        return RudiMetadataInfo(
            api_version=check_rudi_version(o.get("api_version")),  # type: ignore
            metadata_dates=RudiDates.from_json(o.get("metadata_dates")),
            metadata_provider=metadata_provider,
            metadata_contacts=metadata_contacts,
            metadata_source=o.get("metadata_source"),
        )


if __name__ == "__main__":  # pragma: no cover
    tests = "RudiDatasetSize tests"
    log_d(tests, "RudiDatasetSize(4,5)", RudiDatasetSize(4, "5"))  # type: ignore
    log_d(
        tests,
        "RudiDatasetSize.deserialize",
        RudiDatasetSize.from_json({"number_of_records": "4", "number_of_fields": 5}),
    )
    tests = "RudiDataTemporalSpread tests"
    log_d(tests, "RudiDataTemporalSpread()", RudiDataTemporalSpread(Date.now_iso_str()))
    log_d(
        tests,
        "RudiDataTemporalSpread.deserialize",
        RudiDataTemporalSpread.from_json(
            {
                "start_date": "2023-06-12T15:40:11+02:00",
                "end_date": "2023-06-13T11:43:16+02:00",
            }
        ),
    )
