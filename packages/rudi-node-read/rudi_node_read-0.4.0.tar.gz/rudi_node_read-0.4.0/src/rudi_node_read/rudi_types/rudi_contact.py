from uuid import UUID

from rudi_node_read.utils.log import log_d
from rudi_node_read.utils.serializable import Serializable
from rudi_node_read.utils.type_dict import check_has_key, check_is_dict
from rudi_node_read.utils.type_string import (
    check_is_email,
    check_is_string,
    check_is_string_or_none,
    check_is_uuid4,
    uuid4_str,
)


class RudiContact(Serializable):
    def __init__(
        self,
        contact_id: str | UUID,
        contact_name: str,
        email: str,
        contact_summary: str | None = None,
        organization_name: str | None = None,
        collection_tag: str | None = None,
    ):
        self.contact_id = check_is_uuid4(contact_id)
        self.contact_name = check_is_string(contact_name)
        self.email = check_is_email(email)
        self.contact_summary = check_is_string_or_none(contact_summary)
        self.organization_name = check_is_string_or_none(organization_name)
        self.collection_tag = check_is_string_or_none(collection_tag)

    @staticmethod
    def from_json(o: dict):
        check_is_dict(o)
        return RudiContact(
            contact_id=check_has_key(o, "contact_id"),
            contact_name=check_has_key(o, "contact_name"),
            email=check_has_key(o, "email"),
            contact_summary=o.get("contact_summary"),
            organization_name=o.get("organization_name"),
            collection_tag=o.get("collection_tag"),
        )


if __name__ == "__main__":  # pragma: no cover
    tests = "RudiContact tests"
    a_contact = RudiContact(
        contact_id=uuid4_str(),
        contact_name="Test contact",
        email="contact@irisa.fr",
        organization_name="IRISA",
    )
    log_d(tests, "a_contact", a_contact)
    log_d(tests, "a_contact.to_json", a_contact.to_json())
    log_d(tests, "a_contact.to_json_str", a_contact.to_json_str())
    b_contact = RudiContact(
        contact_id=a_contact.contact_id,
        contact_name="Test contact",
        email="contact@irisa.fr",
        organization_name="IRISA",
    )
    log_d(tests, "b_contact", b_contact)
    log_d(tests, "a_contact == b_contact", a_contact == b_contact)
    b_contact.contact_id = uuid4_str()
    log_d(tests, "a_contact == b_contact", a_contact == b_contact)
    log_d(tests, "contacts", a := [a_contact, b_contact])
    log_d(tests, "contacts", a)
