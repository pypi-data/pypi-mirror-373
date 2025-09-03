from builtins import staticmethod

from rudi_node_read.utils.log import log_d
from rudi_node_read.utils.serializable import Serializable
from rudi_node_read.utils.type_date import Date
from rudi_node_read.utils.type_dict import check_is_dict


class RudiDates(Serializable):
    def __init__(
        self,
        created: str | None = None,
        updated: str | None = None,
        validated: str | None = None,
        published: str | None = None,
        expires: str | None = None,
        deleted: str | None = None,
    ):
        self.created: Date = Date.from_str(created, Date.now_iso_str())  # type: ignore
        self.updated: Date = Date.from_str(updated, Date.now_iso_str())  # type: ignore
        if self.created > self.updated:  # type: ignore
            upd = self.updated
            self.updated = self.created
            self.created = upd
        self.validated = Date.from_str(validated)
        self.published = Date.from_str(published)
        self.expires = Date.from_str(expires)
        self.deleted = Date.from_str(deleted)

    @staticmethod
    def from_json(o: dict | None):
        if o is None:
            return RudiDates()
        check_is_dict(o)
        return RudiDates(
            created=o.get("created"),
            updated=o.get("updated"),
            validated=o.get("validated"),
            published=o.get("published"),
            expires=o.get("expires"),
            deleted=o.get("deleted"),
        )


if __name__ == "__main__":  # pragma: no cover
    tests = "RudiDates tests"
    log_d(tests, "empty", RudiDates())
    default_rudi_dates = RudiDates(updated="2023-02-10T14:32:06+02:00")
    log_d(tests, "created", default_rudi_dates.created)
    log_d(tests, "is validated None", default_rudi_dates.validated is None)
    log_d(tests, "default_rudi_dates", default_rudi_dates)
    default_rudi_dates_json = default_rudi_dates.to_json()
    log_d(tests, "default_rudi_dates.to_json()", default_rudi_dates_json)
    assert isinstance(default_rudi_dates_json, dict)
    log_d(tests, "RudiDates.deserialize", RudiDates.from_json(default_rudi_dates_json))
