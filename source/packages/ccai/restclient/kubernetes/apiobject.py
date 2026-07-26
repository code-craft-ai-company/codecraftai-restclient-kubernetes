"""
    .. module:: apiobject
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: :class:`ApiObject` — a dict that is also attribute
               addressable, so API-server JSON reads like the object model
               callers are used to.

    The Kubernetes API server returns JSON whose field names are camelCase
    (``gitVersion``, ``creationTimestamp``).  Code written against the
    official SDK reads snake_case attributes (``git_version``).  An
    :class:`ApiObject` answers BOTH — ``obj["gitVersion"]``,
    ``obj.gitVersion`` and ``obj.git_version`` all resolve — so a consumer
    can migrate off the SDK without rewriting every field access, and new
    code can use whichever spelling reads better.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List


def _camel_to_snake(name: str) -> str:
    """
        Convert a camelCase field name to snake_case.

        :param name: The camelCase name.

        :returns: The snake_case equivalent.
    """
    characters: List[str] = []
    for character in name:
        if character.isupper() is True:
            if len(characters) > 0:
                characters.append("_")
            characters.append(character.lower())
        else:
            characters.append(character)
    rtnval = "".join(characters)
    return rtnval


def wrap_api_value(value: Any) -> Any:
    """
        Wrap a decoded JSON value so nested objects are attribute
        addressable.

        :param value: The decoded JSON value.

        :returns: An :class:`ApiObject` for dicts, a list of wrapped values
            for lists, or the value unchanged.
    """
    if isinstance(value, dict) is True:
        rtnval = ApiObject(value)
        return rtnval
    if isinstance(value, list) is True:
        rtnval = [wrap_api_value(item) for item in value]
        return rtnval
    rtnval = value
    return rtnval


class ApiObject(dict):
    """
        A ``dict`` of API-server JSON that is also attribute addressable.

        Attribute lookup accepts the wire spelling (``gitVersion``) and the
        snake_case spelling (``git_version``).  A missing field returns
        ``None`` rather than raising, matching how the SDK's optional
        fields behave and keeping ``getattr(obj, "field", None)`` guards in
        consumer code correct.

        Kubernetes list responses carry their contents under ``items`` —
        which collides with ``dict.items``.  The API field WINS on attribute
        access, because ``response.items`` reading the resource list is the
        whole point and is what SDK-era consumer code expects; the mapping
        method remains reachable as :meth:`dict_items` and by the usual
        ``dict.items(obj)`` spelling.
    """

    # Field names whose API meaning must win over an inherited dict method.
    _SHADOWING_FIELDS = ("items", "keys", "values", "copy", "get",
                         "update", "clear", "pop")

    def __getattribute__(self, name: str) -> Any:
        """
            Resolve attribute access, letting API fields shadow the dict
            methods they collide with.

            :param name: The attribute name.

            :returns: The field value when the name is a shadowing API
                field present in the payload, otherwise normal attribute
                resolution.
        """
        if name in ApiObject._SHADOWING_FIELDS:
            if dict.__contains__(self, name) is True:
                rtnval = wrap_api_value(dict.__getitem__(self, name))
                return rtnval
        rtnval = object.__getattribute__(self, name)
        return rtnval

    def dict_items(self):
        """
            Return the underlying mapping's items view.

            Provided because ``items`` is also a Kubernetes list field and
            the API meaning wins on attribute access.

            :returns: The mapping items view.
        """
        rtnval = dict.items(self)
        return rtnval

    def __getattr__(self, name: str) -> Any:
        """
            Resolve a field by attribute access.

            :param name: The field name, in wire or snake_case spelling.

            :returns: The wrapped field value, or ``None`` when absent.
        """
        if name in self:
            rtnval = wrap_api_value(self[name])
            return rtnval

        for key in dict.keys(self):
            if _camel_to_snake(key) == name:
                rtnval = wrap_api_value(self[key])
                return rtnval

        rtnval = None
        return rtnval

    def __setattr__(self, name: str, value: Any) -> None:
        """
            Set a field by attribute assignment.

            :param name: The field name.
            :param value: The value to store.

            :returns: ``None``
        """
        self[name] = value
        return

    def as_dict(self) -> Dict[str, Any]:
        """
            Return the underlying plain dictionary.

            :returns: The wire-shaped dictionary.
        """
        rtnval = {key: dict.__getitem__(self, key)
                  for key in dict.keys(self)}
        return rtnval
