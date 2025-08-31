import json
from abc import ABC  # , abstractmethod
from datetime import datetime

from .mini_logger import MiniLogger as logger


# TODO Where are we using it? Shall we extend the usage of OurObject as the father of all our entities?
class OurObject(ABC):

    entity_name = None
    id = None

    # Needed by print_our_object_with_id()
    name = None
    number = None

    fields = {
        # Needed by print_our_object_with_id()
        "name",
        "number"
    }

    def __init__(self, entity_name: str = None, id: int = None, **kwargs):
        INIT_METHOD_NAME = '__init__'
        logger.start(INIT_METHOD_NAME, object={'kwargs': kwargs})
        self.set_entity_name(entity_name)
        self.set_id(id)
        self.kwargs = kwargs
        logger.end(INIT_METHOD_NAME, object={'kwargs': kwargs})

    def __convert_kwargs_to_fields(self, kwargs, fields):
        for field, value in kwargs.items():
            if field in fields:
                setattr(self, field, value)

    # TODO Do we need it?
    def __convert_fields_to_kwargs(self, fields, kwargs):
        for field in fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])
            else:
                setattr(self, field, None)

    def set_entity_name(self, entity_name: str) -> None:
        self.entity_name = entity_name

    def get_id_column_name(self) -> str:
        """Returns the name of the column that is used as the id of the object"""
        id_column_name = self.entity_name + "_id"
        return id_column_name

    def set_id(self, id: int) -> None:
        self.id = id

    def get_id(self) -> int:
        return self.id

    # Commented so we can use it in database foreach()
    # @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the object"""
        # raise NotImplementedError(
        #     "Subclasses must implement the 'get_name' method.")

    def get(self, attr_name: str) -> None:
        """Returns the value of the attribute with the given name"""
        GET_METHOD_NAME = 'get'
        logger.start(GET_METHOD_NAME, object={'attr_name': attr_name})
        arguments = getattr(self, 'kwargs', None)
        value = arguments.get(attr_name, None)
        logger.end(GET_METHOD_NAME, object={'attr_name': attr_name})
        return value

    def get_all_arguments(self):
        """Returns all the arguments passed to the constructor as a dictionary"""
        get_all_arguments_result = getattr(self, 'kwargs', None)
        return get_all_arguments_result

    def to_json(self) -> str:
        """This is backwards compatible with the previous implementation"""
        to_json_result = self.to_json_str()
        return to_json_result

    def to_json_dict(self) -> str:
        """Returns a json string representation of this object"""
        json_str = self.to_json_str()
        json_dict = json.loads(json_str)

        return json_dict

    def to_json_str(self) -> str:
        """Returns a json string representation of this object"""
        to_json_str_result = json.dumps(self.__dict__, default=self._serialize)
        return to_json_str_result

    @staticmethod
    def _serialize(obj):
        """Custom serialization function for unsupported types. Used by json.dumps"""
        if isinstance(obj, datetime):
            return obj.isoformat()  # Converts datetime to ISO 8601 string
        raise TypeError(f"Type {type(obj)} not serializable")

    def from_json(self, json_string: str) -> 'OurObject':
        """Returns an instance of the class from a json string"""
        FROM_JSON_METHOD_NAME = 'from_json'
        logger.start(FROM_JSON_METHOD_NAME,
                     object={'json_string': json_string})
        self.__dict__ = json.loads(json_string)
        logger.end(FROM_JSON_METHOD_NAME,
                   object={'json_dict': self.__dict__})
        return self

    def __eq__(self, other) -> bool:
        """Checks if two objects are equal"""
        if not isinstance(other, OurObject):
            return False
        eq_result = self.__dict__ == other.__dict__
        return eq_result

    def __ne__(self, other) -> bool:
        """Checks if two objects are not equal"""
        ne_result = not self.__eq__(other)
        return ne_result

    def __str__(self):
        str_result = self.entity_name + ": " + str(self.__dict__)
        return str_result

    def __repr__(self):
        # TODO make sure both of them is not None
        repr_result = self.entity_name + ": " + str(self.__dict__)
        return repr_result

    def to_dict(self):
        return self.__dict__
