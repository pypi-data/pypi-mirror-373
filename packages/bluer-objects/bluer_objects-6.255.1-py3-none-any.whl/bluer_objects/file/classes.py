from typing import Any
import datetime
import json


# https://gist.github.com/jsbueno/9b2ea63fb16b84658281ec29b375283e
class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            pass

        if obj.__class__.__name__ == "ndarray":
            return obj.tolist()

        if isinstance(obj, datetime.datetime):
            return "{}".format(obj)

        return (
            obj.__dict__
            if not hasattr(type(obj), "__json_encode__")
            else obj.__json_encode__
        )


def as_json(
    thing: Any,
) -> str:
    # https://docs.python.org/2/library/json.html
    return json.dumps(
        thing,
        sort_keys=True,
        cls=JsonEncoder,
        indent=0,
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("\n", "")
