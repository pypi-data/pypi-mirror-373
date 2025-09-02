from typing import Any, Optional, Dict, Tuple, Text, List


class ClassUtil:
    @staticmethod
    def merge(class_a:Any, class_b:Any) -> Any:
        class_a.__dict__.update(class_b.__dict__)
        return class_a
    

    @staticmethod
    def get_class_name(cls:Any) -> str:
       return cls.__name__ if cls is not None else ""


    @staticmethod
    def get_class_instance_name(cls:Any) -> str:
       return cls.__class__.__name__ if cls is not None else ""


    @staticmethod
    def get_class_names(model: Any) -> List[str]:
        class_names = set()

        # Add class name of the model itself
        class_names.add(type(model).__name__)

        # Get attributes of the model
        try:
            attributes = vars(model)
        except TypeError:
            # model has no __dict__ (e.g. primitive)
            return List(class_names)

        for attr_name, attr_value in attributes.items():
            if attr_value is None:
                continue

            # Check if it's a list and has elements
            if isinstance(attr_value, list) and len(attr_value) > 0:
                first_elem = attr_value[0]
                elem_class_name = type(first_elem).__name__
                if elem_class_name not in ["dict", "list", "str", "int", "float", "bool"]:
                    class_names.add(elem_class_name)

            # Check if it's another object (not primitive, not list)
            elif hasattr(attr_value, "__dict__"):
                value_class_name = type(attr_value).__name__
                if value_class_name not in ["dict", "list", "str", "int", "float", "bool"]:
                    class_names.add(value_class_name)

        return list(class_names)