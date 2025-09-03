import json
import datetime

from airs.core.models.model import Item


def serialize_datetime(obj): 
    if isinstance(obj, datetime.datetime):
        return int(obj.timestamp())
    raise TypeError("Type not serializable")


def to_airs_item(item: Item) -> Item:
    """ Takes an item and makes sure to map the namespace fields to AIRS Item. Keys can contain : as namespace seperator

     Args:
         item (Item): The item (with : namespace separator)

     Returns:
         item: The airs item
     """
    dictionary = item.model_dump(exclude_unset=True, by_alias=True, exclude_none=True)
    return Item(**__replaceKeys(dictionary, ":", "__"))


def to_dict(item: Item) -> dict:
    """ create a dictionnary from the Item. Keys contain : as namespace seperator

     Args:
         item (Item): The item

     Returns:
         dict: The dictionary. Keys contain : as namespace seperator
     """
    dictionary = item.model_dump(exclude_unset=True, by_alias=True, exclude_none=True)
    return __replaceKeys(dictionary, "__", ":")


def to_airs_dict(item: Item) -> dict:
    """ create a dictionnary from the Item. Keys contain __ as namespace seperator

    Args:
        item (Item): The item

    Returns:
        dict: The dictionary. Keys contain __ as namespace seperator
    """
    dictionary = item.model_dump(exclude_unset=True, by_alias=False, exclude_none=True)
    return dictionary


def to_airs_json(item: Item) -> str:
    """ create a json from the Item. Keys contain __ as namespace seperator

    Args:
        item (Item): The item

    Returns:
        str: the json. Keys contain __ as namespace seperator
    """
    return json.dumps(to_airs_dict(item), indent=2, default=serialize_datetime)


def to_json(item: Item) -> str:
    """ create a json from the Item. Keys contain : as namespace seperator

    Args:
        item (Item): The item

    Returns:
        str: the json. Keys contain : as namespace seperator
    """
    return json.dumps(to_dict(item), indent=2, default=serialize_datetime)


def item_from_json_file(jsonfile) -> Item:
    """ load a json file containing an Item

    Args:
        jsonfile (file): the json file

    Returns:
        Item: _description_
    """
    return Item(**__replaceKeys(json.load(jsonfile), ":", "__"))


def item_from_json(json_string: str) -> Item:
    """ load a json Item

    Args:
        json_string (str): the Item as json

    Returns:
        Item: the Item
    """
    return Item(**__replaceKeys(json.loads(json_string), ":", "__"))


def item_from_dict(object: dict) -> Item:
    """ load a dict Item

    Args:
        object (dict): the Item as dict

    Returns:
        Item: the Item
    """
    return Item(**__replaceKeys(object, ":", "__"))


def __replaceKeys(o, before: str, after: str):
    if type(o) is dict:
        d = {}
        for key in o:
            d[key.replace(before, after)] = __replaceKeys(o[key], before, after)
        return d
    if type(o) is list:
        return list(map(lambda elt: __replaceKeys(elt, before, after), o))
    else:
        return o
