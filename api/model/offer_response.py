# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = offers_from_dict(json.loads(json_string))

from typing import Any, List, TypeVar, Type, cast, Callable
import shopping_list_complex_model as slc

T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def offers_from_dict(s: Any) -> List[slc.Offer]:
    return from_list(slc.Offer.from_dict, s)


def offers_to_dict(x: List[slc.Offer]) -> Any:
    return from_list(lambda x: to_class(slc.Offer, x), x)
