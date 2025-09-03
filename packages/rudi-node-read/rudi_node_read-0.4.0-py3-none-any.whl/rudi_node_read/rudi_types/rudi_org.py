from uuid import UUID

from rudi_node_read.utils.log import log_d
from rudi_node_read.utils.serializable import Serializable
from rudi_node_read.utils.type_dict import check_has_key, check_is_dict, safe_get_key
from rudi_node_read.utils.type_string import check_is_uuid4, uuid4_str


class RudiOrganization(Serializable):
    def __init__(
        self,
        organization_id: str | UUID,
        organization_name: str,
        organization_caption: str | None = None,
        organization_summary: str | None = None,
        organization_address: str | None = None,
        organization_coordinates: dict | None = None,
        collection_tag: str | None = None,
    ):
        self.organization_id = check_is_uuid4(organization_id)
        self.organization_name = organization_name
        self.organization_caption = organization_caption
        self.organization_summary = organization_summary
        self.organization_address = organization_address

        latitude = safe_get_key(organization_coordinates, "latitude")
        longitude = safe_get_key(organization_coordinates, "longitude")
        self.organization_coordinates = (
            None if latitude is None or longitude is None else {"latitude": latitude, "longitude": longitude}
        )
        self.collection_tag = collection_tag

    @staticmethod
    def from_json(o: dict):
        check_is_dict(o)
        latitude = safe_get_key(o, "organization_coordinates", "latitude")
        longitude = safe_get_key(o, "organization_coordinates", "longitude")
        organization_coordinates = (
            None if latitude is None and longitude is None else {"latitude": latitude, "longitude": longitude}
        )

        return RudiOrganization(
            organization_id=check_is_uuid4(check_has_key(o, "organization_id")),
            organization_name=check_has_key(o, "organization_name"),
            organization_caption=o.get("organization_caption"),
            organization_summary=o.get("organization_summary"),
            organization_address=o.get("organization_address"),
            organization_coordinates=organization_coordinates,
            collection_tag=o.get("collection_tag"),
        )


if __name__ == "__main__":  # pragma: no cover
    my_org = RudiOrganization(
        organization_id=uuid4_str(),
        organization_name="IRISA",
        organization_address="263 avenue du Général Leclerc, 35000 RENNES",
        organization_coordinates={"longitude": 1.456, "latitude": 0},
    )
    log_d(
        "RudiOrganization",
        "constructor",
        RudiOrganization(
            organization_id=uuid4_str(),
            organization_name="IRISA",
            organization_address="263 avenue du Général Leclerc, 35000 RENNES",
            organization_coordinates={"longitude": 1.456, "latitude": 0},
        ),
    )
    log_d(
        "RudiOrganization",
        "make_producer",
        RudiOrganization.from_json(
            {
                "organization_id": uuid4_str(),
                "organization_name": "IRISA",
                "organization_address": "263 avenue du Général Leclerc, 35000 RENNES",
                "organization_coordinates": {"longitude": 1.456, "latitude": 0},
            }
        ),
    )

    log_d(
        "RudiOrganization",
        "make basic producer",
        RudiOrganization.from_json({"organization_id": uuid4_str(), "organization_name": "Noorg"}),
    )
