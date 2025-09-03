def get_attribute_type(model_instance, attribute_name: str):
    """
    Get the outer and inner types of an attribute in a Pydantic model instance even if value is still None and handling
    nested attributes with dot-separated indexing.

    Args:
        model_instance: An instance of a Pydantic model.
        attribute_name: A string representing the attribute name, using dot-separated indexing for nested attributes (e.g., "nested_model.attribute").

    Returns:
        A list containing two elements:
            - The outer type of the attribute (e.g., typing.List for a list attribute).
            - The inner type of the attribute (e.g., <class 'float'> for a float attribute).

    Raises:
        KeyError: If the attribute_name is not found in the model_instance.
        AttributeError: If a nested attribute in attribute_name is not found in the model_instance.
    """
    if "." in attribute_name:
        first_attr, rest = attribute_name.split(".", 1)
        nested_model_instance = getattr(model_instance, first_attr)
        return get_attribute_type(nested_model_instance, rest)
    else:
        return model_instance.__annotations__[attribute_name]
