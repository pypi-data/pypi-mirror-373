from abc import ABC, abstractmethod
from json import dumps

from rudi_node_read.utils.log import log_d, log_e
from rudi_node_read.utils.type_list import clean_nones
from rudi_node_read.utils.typing_utils import get_type_name


def is_serializable(o):
    return isinstance(o, Serializable)


def is_jsonable(o):
    try:
        dumps(o)
        return True
    except (TypeError, OverflowError) as e:
        log_e("is_jsonable", f"Type {get_type_name(o)} not jsonable", e)
        return False


class Serializable(ABC):
    @property
    def class_name(self):
        return self.__class__.__name__

    def __eq__(self, other):  # NOSONAR
        here = f"{self.class_name}._eq_"
        if other is None:
            log_d(here, f"Target is null. {self} ≠ {other}")
            return False
        if not isinstance(other, Serializable):
            # log_d(here, f"Type '{get_type_name(other)}' is not serializable. {self} ≠ {other}")
            return False
        self_json = self.to_json()
        other_json = other.to_json()
        if not isinstance(self_json, type(other_json)):
            return False
        if isinstance(self_json, list) and isinstance(other_json, list):
            return sorted(self_json) == sorted(other_json)
        if isinstance(self_json, dict) and isinstance(other_json, dict):
            for key in self_json.keys():
                if (val_b := other_json.get(key)) is None:
                    log_d(here, f"key does not exist in target: '{key}'")
                    return False
                else:
                    if (val_a := self_json[key]) != val_b:
                        log_d(here, f"values differ for key '{key}': {val_a} != {val_b}")
                        return False
                other_json.pop(key)
            if other_json == {}:
                return True
            log_d(here, f"target still has some unmatched keys: {other_json}")
            return False
        return self_json == other_json

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        # log_d(f'{self.class_name}.__repr__', self.class_name)
        return str(self.to_json_str())

    def __str__(self) -> str:
        # log_d(f'{self.class_name}.__str__', self.class_name)
        return str(self.to_json_str())

    def to_json_str(self, keep_nones: bool = False, ensure_ascii: bool = False, sort_keys: bool = False) -> str:
        """
        Makes sure every attribute can be serialized.
        :return: a JSON representation of the object as a string
        """
        self_dict = self.__dict__ if keep_nones else clean_nones(self.__dict__)

        def default_dumps(o):  # pragma: no cover
            if isinstance(o, Serializable):
                return o.to_json(keep_nones)
            elif not isinstance(o, dict):
                return str(o)
            else:
                return o.__dict__ if keep_nones else clean_nones(o.__dict__)

        return dumps(
            self_dict,
            sort_keys=sort_keys,
            default=default_dumps,
            ensure_ascii=ensure_ascii,
        )

    def to_json(self, keep_nones: bool = False) -> dict | list | str:
        """
        Transform the object into a Python (JSON compatible) object
        :return: a Python object
        """
        if isinstance(self, list):
            self_list = []
            for elt in self:
                if isinstance(elt, Serializable):
                    self_list.append(elt.to_json())
                else:
                    self_list.append(elt)
            return self_list

        self_dict: dict = self.__dict__ if keep_nones else clean_nones(self.__dict__)  # type: ignore
        out_json_dict = {}
        for key in self_dict:
            val = self_dict[key]
            if isinstance(val, (str, int)):
                out_json_dict[key] = val
            elif isinstance(val, Serializable):
                out_json_dict[key] = val.to_json(keep_nones)
            elif isinstance(val, list):
                out_json_dict[key] = [
                    (sub_val.to_json(keep_nones) if isinstance(val, Serializable) else sub_val) for sub_val in val
                ]
            elif isinstance(val, dict):
                out_json_dict[key] = {}
                for sub_key, sub_val in val.items():
                    out_json_dict[key][sub_key] = (
                        sub_val.to_json(keep_nones) if isinstance(sub_val, Serializable) else sub_val
                    )
            else:
                out_json_dict[key] = val.to_json(keep_nones) if isinstance(val, Serializable) else val
        return out_json_dict

    @staticmethod
    @abstractmethod
    def from_json(o: dict):
        raise NotImplementedError()
