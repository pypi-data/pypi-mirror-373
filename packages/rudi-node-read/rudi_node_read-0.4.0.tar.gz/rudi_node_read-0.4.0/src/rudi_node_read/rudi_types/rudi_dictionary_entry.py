from json import dumps

from rudi_node_read.rudi_types.defaults.meta_defaults import DEFAULT_LANG
from rudi_node_read.rudi_types.rudi_const import (
    RECOGNIZED_LANGUAGES,
    Language,
    check_is_literal,
)
from rudi_node_read.utils.log import log_d
from rudi_node_read.utils.serializable import Serializable
from rudi_node_read.utils.type_dict import check_has_key, check_is_dict
from rudi_node_read.utils.type_list import are_list_equal
from rudi_node_read.utils.type_string import check_is_string
from rudi_node_read.utils.typing_utils import get_type_name


class RudiDictionaryEntry(Serializable):
    def __init__(self, lang: Language, text: str):
        if lang is None:
            raise ValueError("parameter 'lang' cannot be null.")
        if text is None:
            raise ValueError("parameter 'text' cannot be null.")
        self.lang: Language = check_is_literal(lang, RECOGNIZED_LANGUAGES, "parameter is not a recognized language")
        self.text: str = check_is_string(text)

    @staticmethod
    def from_json(o: dict | str):
        if isinstance(o, str):
            return RudiDictionaryEntry(lang=DEFAULT_LANG, text=o)
        check_is_dict(o)
        lang = check_is_literal(
            check_has_key(o, "lang")[0:2],
            RECOGNIZED_LANGUAGES,
            "parameter is not a recognized language",
        )
        text = check_is_string(check_has_key(o, "text"))
        return RudiDictionaryEntry(lang=lang, text=text)


class RudiDictionaryEntryList(Serializable, list):
    def __init__(self, list_entries: list[RudiDictionaryEntry]):
        if not isinstance(list_entries, list):
            raise ValueError("input parameter should be a list")
        super().__init__()
        for entry in list_entries:
            if isinstance(entry, RudiDictionaryEntry):
                self.append(RudiDictionaryEntry(lang=entry.lang, text=entry.text))

    def __eq__(self, other=None):
        here = f"{self.class_name}.eq"
        if other is None:
            log_d(here, f"Target is null. {self} ≠ {other}")
            return False
        if not isinstance(other, RudiDictionaryEntryList):
            log_d(here, f"Type '{get_type_name(other)}' is not a RudiDictionaryEntryList. {self} ≠ {other}")
            return False
        return are_list_equal(self, other, ignore_order=True)

    def to_json_str(
        self,
        keep_nones: bool = False,
        ensure_ascii: bool = False,
        sort_keys: bool = False,
    ) -> str:
        return dumps([entry.to_json() for entry in self], ensure_ascii=ensure_ascii, sort_keys=sort_keys)

    def to_json(self, keep_nones: bool = False) -> list:  # type: ignore
        """
        Transform the object into a Python object
        :return: a Python object
        """
        return [entry.to_json() for entry in self]

    @staticmethod
    def from_json(o: None | list | dict | str | RudiDictionaryEntry):
        if o is None:
            return None
        if isinstance(o, str):
            return RudiDictionaryEntryList([RudiDictionaryEntry(lang=DEFAULT_LANG, text=o)])
        if isinstance(o, dict):
            return RudiDictionaryEntryList([RudiDictionaryEntry.from_json(o)])
        if isinstance(o, RudiDictionaryEntry):
            return RudiDictionaryEntryList([o])
        if not isinstance(o, list):
            raise TypeError(f"input parameter should be a list, got {type(o)}")

        return RudiDictionaryEntryList([RudiDictionaryEntry.from_json(entry) for entry in o])


if __name__ == "__main__":  # pragma: no cover
    tests = "RudiDictionaryEntry tests"
    dico1 = RudiDictionaryEntry("en", "quite something")
    log_d(tests, dico1)
    log_d(tests, dico1.to_json())
    dico2 = RudiDictionaryEntry.from_json("quite something")
    log_d(tests, dico2)
    log_d(tests, dico2.to_json())
    dico_list = RudiDictionaryEntryList.from_json("quite something")
    log_d(tests, dico_list)
    log_d(tests, isinstance(dico_list, list))
    if dico_list is not None:
        log_d(tests, dico_list.to_json())
