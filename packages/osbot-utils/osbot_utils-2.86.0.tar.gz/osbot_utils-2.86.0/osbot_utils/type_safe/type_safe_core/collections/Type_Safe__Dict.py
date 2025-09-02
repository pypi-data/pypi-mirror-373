from typing                                                           import Type
from osbot_utils.type_safe.Type_Safe__Base                            import Type_Safe__Base
from osbot_utils.type_safe.Type_Safe__Primitive import Type_Safe__Primitive
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List import Type_Safe__List


class Type_Safe__Dict(Type_Safe__Base, dict):
    def __init__(self, expected_key_type, expected_value_type, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.expected_key_type   = expected_key_type
        self.expected_value_type = expected_value_type

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)                                     # First try direct lookup
        except KeyError:
            converted_key = self.try_convert(key, self.expected_key_type)       # Try converting the key
            return super().__getitem__(converted_key)                           # and compare again

    def __setitem__(self, key, value):                                          # Check type-safety before allowing assignment.
        key   = self.try_convert(key  , self.expected_key_type  )
        value = self.try_convert(value, self.expected_value_type)
        self.is_instance_of_type(key  , self.expected_key_type)
        self.is_instance_of_type(value, self.expected_value_type)
        super().__setitem__(key, value)

    def __enter__(self): return self
    def __exit__ (self, type, value, traceback): pass

    def json(self):                                                                         # Convert the dictionary to a JSON-serializable format.
        from osbot_utils.type_safe.Type_Safe import Type_Safe                               # can only import this here to avoid circular imports

        result = {}
        for key, value in self.items():

            if isinstance(key, (type, Type)):                                                     # Handle Type objects as keys
                key = f"{key.__module__}.{key.__name__}"
            elif isinstance(key, Type_Safe__Primitive):
                key = key.__to_primitive__()
            if isinstance(value, Type_Safe):                                                # Handle Type_Safe objects in values
                result[key] = value.json()
            elif isinstance(value, (list, tuple)):                                          # Handle lists/tuples that might contain Type_Safe objects
                result[key] = [item.json() if isinstance(item, Type_Safe) else item
                               for item in value]
            elif isinstance(value, dict):                                                   # Handle nested dictionaries that might contain Type_Safe objects
                result[key] = {k: v.json() if isinstance(v, Type_Safe) else v
                               for k, v in value.items()}
            else:
                if isinstance(value, Type_Safe__Primitive):
                    result[key] = value.__to_primitive__()
                else:
                    result[key] = value
        return result

    def keys(self) -> Type_Safe__List:
        return Type_Safe__List(self.expected_key_type, super().keys())

    def values(self) -> Type_Safe__List:
        return Type_Safe__List(self.expected_value_type, super().values())