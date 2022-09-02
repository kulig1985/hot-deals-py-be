# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = offer_model_list_from_dict(json.loads(json_string))

from typing import Any, List, TypeVar, Type, cast, Callable


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


class ID:
    oid: str

    def __init__(self, oid: str) -> None:
        self.oid = oid

    @staticmethod
    def from_dict(obj: Any) -> 'ID':
        assert isinstance(obj, dict)
        oid = from_str(obj.get("$oid"))
        return ID(oid)

    def to_dict(self) -> dict:
        result: dict = {}
        result["$oid"] = from_str(self.oid)
        return result


class OfferListenerEntity:
    id: ID
    uid: str
    item_name: str
    cr_date: str
    bool_id: int
    mod_date: None
    image_color_index: int
    shopping_list_id: str
    check_flag: int
    item_count: int

    def __init__(self, id: ID, uid: str, item_name: str, cr_date: str, bool_id: int, mod_date: None, image_color_index: int,
                 shopping_list_id: str, check_flag: int, item_count: int) -> None:
        self.id = id
        self.uid = uid
        self.item_name = item_name
        self.cr_date = cr_date
        self.bool_id = bool_id
        self.mod_date = mod_date
        self.image_color_index = image_color_index
        self.shopping_list_id = shopping_list_id
        self.check_flag = check_flag
        self.item_count = item_count

    @staticmethod
    def from_dict(obj: Any) -> 'OfferListenerEntity':
        assert isinstance(obj, dict)
        id = ID.from_dict(obj.get("_id"))
        uid = from_str(obj.get("uid"))
        item_name = from_str(obj.get("itemName"))
        cr_date = from_str(obj.get("crDate"))
        bool_id = from_int(obj.get("boolId"))
        mod_date = from_none(obj.get("modDate"))
        image_color_index = from_int(obj.get("imageColorIndex"))
        shopping_list_id = from_str(obj.get("shoppingListId"))
        check_flag = from_int(obj.get("checkFlag"))
        item_count = from_int(obj.get("itemCount"))
        return OfferListenerEntity(id, uid, item_name, cr_date, bool_id, mod_date, image_color_index, shopping_list_id,
                                   check_flag, item_count)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = to_class(ID, self.id)
        result["uid"] = from_str(self.uid)
        result["itemName"] = from_str(self.item_name)
        result["crDate"] = from_str(self.cr_date)
        result["boolId"] = from_int(self.bool_id)
        result["modDate"] = from_none(self.mod_date)
        result["imageColorIndex"] = from_int(self.image_color_index)
        result["shoppingListId"] = from_str(self.shopping_list_id)
        result["checkFlag"] = from_int(self.check_flag)
        result["itemCount"] = from_int(self.item_count)
        return result


class Offer:
    id: ID
    item_id: int
    item_name: str
    item_clean_name: str
    image_url: str
    price: int
    measure: str
    sales_start: str
    source: str
    run_date: str
    shop_name: str
    is_sales: int
    insert_type: str
    time_key: str
    image_color_index: int
    is_selected_flag: int
    selected_by: str

    def __init__(self, id: ID, item_id: int, item_name: str, item_clean_name: str, image_url: str, price: int, measure: str, sales_start: str, source: str, run_date: str, shop_name: str, is_sales: int, insert_type: str, time_key: str, image_color_index: int, is_selected_flag: int, selected_by: str) -> None:
        self.id = id
        self.item_id = item_id
        self.item_name = item_name
        self.item_clean_name = item_clean_name
        self.image_url = image_url
        self.price = price
        self.measure = measure
        self.sales_start = sales_start
        self.source = source
        self.run_date = run_date
        self.shop_name = shop_name
        self.is_sales = is_sales
        self.insert_type = insert_type
        self.time_key = time_key
        self.image_color_index = image_color_index
        self.is_selected_flag = is_selected_flag
        self.selected_by = selected_by

    @staticmethod
    def from_dict(obj: Any) -> 'Offer':
        assert isinstance(obj, dict)
        id = ID.from_dict(obj.get("_id"))
        item_id = from_union([from_int, lambda x: int(from_str(x))], obj.get("itemId"))
        item_name = from_str(obj.get("itemName"))
        item_clean_name = from_str(obj.get("itemCleanName"))
        image_url = from_str(obj.get("imageUrl"))
        price = from_int(obj.get("price"))
        measure = from_str(obj.get("measure"))
        sales_start = from_str(obj.get("salesStart"))
        source = from_str(obj.get("source"))
        run_date = from_str(obj.get("runDate"))
        shop_name = from_str(obj.get("shopName"))
        is_sales = from_int(obj.get("isSales"))
        insert_type = from_str(obj.get("insertType"))
        time_key = from_str(obj.get("timeKey"))
        image_color_index = from_int(obj.get("imageColorIndex"))
        is_selected_flag = from_int(obj.get("isSelectedFlag"))
        selected_by = from_str(obj.get("selectedBy"))
        return Offer(id, item_id, item_name, item_clean_name, image_url, price, measure, sales_start, source, run_date, shop_name, is_sales, insert_type, time_key, image_color_index, is_selected_flag, selected_by)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = to_class(ID, self.id)
        result["itemId"] = from_int(self.item_id)
        result["itemName"] = from_str(self.item_name)
        result["itemCleanName"] = from_str(self.item_clean_name)
        result["imageUrl"] = from_str(self.image_url)
        result["price"] = from_int(self.price)
        result["measure"] = from_str(self.measure)
        result["salesStart"] = from_str(self.sales_start)
        result["source"] = from_str(self.source)
        result["runDate"] = from_str(self.run_date)
        result["shopName"] = from_str(self.shop_name)
        result["isSales"] = from_int(self.is_sales)
        result["insertType"] = from_str(self.insert_type)
        result["timeKey"] = from_str(self.time_key)
        result["imageColorIndex"] = from_int(self.image_color_index)
        result["isSelectedFlag"] = from_int(self.is_selected_flag)
        result["selectedBy"] = from_str(self.selected_by)
        return result


class OfferModelList:
    offer_listener_entity: OfferListenerEntity
    offers: List[Offer]

    def __init__(self, offer_listener_entity: OfferListenerEntity, offers: List[Offer]) -> None:
        self.offer_listener_entity = offer_listener_entity
        self.offers = offers

    @staticmethod
    def from_dict(obj: Any) -> 'OfferModelList':
        assert isinstance(obj, dict)
        offer_listener_entity = OfferListenerEntity.from_dict(obj.get("offerListenerEntity"))
        offers = from_list(Offer.from_dict, obj.get("offers"))
        return OfferModelList(offer_listener_entity, offers)

    def to_dict(self) -> dict:
        result: dict = {}
        result["offerListenerEntity"] = to_class(OfferListenerEntity, self.offer_listener_entity)
        result["offers"] = from_list(lambda x: to_class(Offer, x), self.offers)
        return result


def offer_model_list_from_dict(s: Any) -> OfferModelList:
    return OfferModelList.from_dict(s)

def offer_model_list_to_dict(x: OfferModelList) -> Any:
    return to_class(OfferModelList, x)

def offers_from_dict(s: Any) -> List[Offer]:
    return from_list(Offer.from_dict, s)

def offers_to_dict(x: List[Offer]) -> Any:
    return from_list(lambda x: to_class(Offer, x), x)
