from typing import List, Dict

from qcodes.instrument import Instrument
from qcodes.parameters import Parameter

class QHMetaData(Instrument):
    """
    A QCoDeS Instrument subclass that manages metadata for a dataset within the QHarbor framework.

    This instrument stores tags and attributes, which the synchronization agent will recognize and add as such to the dataset.
    """

    def __init__(self, name : str, static_tags: List[str] = [],
                        static_attributes: Dict[str, str] = {}):
        """
        Initialize a QHMetaData instance.

        Args:
            name (str): The name of the instrument, this should be "qh_meta"
            static_tags (List[str]): A list of static tags that are always included in
                the metadata. These tags remain after the reset method is called.
            static_attributes (Dict[str, str]): A dictionary of static attributes that are
                always included in the metadata. These attributes remain after the reset method is called.
        """
        super().__init__(name)
        
        self._static_tags = static_tags
        self._static_attributes = static_attributes

        self._dynamic_tags = []
        self._dynamic_attributes = {}

        self.add_parameter("tags", get_cmd=self.__get_tags)
        self.add_parameter("attributes", get_cmd=self.__get_attributes)

    def add_tags(self, tags: List[str]) -> None:
        """
        Add dynamic tags to the metadata. These tags will be cleared upon reset.

        Args:
            tags (List[str]): A list of tags to add.
        """
        self._dynamic_tags.extend(tags)

    def add_attributes(self, attributes: Dict[str, str]) -> None:
        """
        Add dynamic attributes to the metadata. These attributes will be cleared upon reset.

        Args:
            attributes (Dict[str, str]): A dictionary of key-value pairs to add as attributes.
        """
        self._dynamic_attributes.update(attributes)

    def reset(self) -> None:
        """
        Clear all dynamic tags and attributes.

        This does not affect static tags or attributes, nor the list of important parameters.
        """
        self._dynamic_tags.clear()
        self._dynamic_attributes.clear()

    def __get_tags(self) -> List[str]:
        """
        Return a combined list of static and dynamic tags.

        Returns:
            List[str]: The current list of tags (static + dynamic).
        """
        return list(set(self._static_tags + self._dynamic_tags))

    def __get_attributes(self) -> Dict[str, str]:
        """
        Return a combined dictionary containing static, dynamic attributes, and parameter values.

        Returns:
            Dict[str, str]: A dictionary with the static and dynamic attributes.
        """
        attr = {**self._static_attributes}
        attr.update(self._dynamic_attributes)
        return attr
    
    def get_idn(self):
        return {'vendor': 'QHarbor', 'model': 'QHarbor Metadata Manager', 'serial': None, 'firmware': None}
    
def validate_parameter(parameter: Parameter) -> Parameter:
    # for when we add parameters to the metadata.
    """
    Validate that a parameter is an instance of qcodes.Parameter and its value is int or float.

    Args:
        parameter (Parameter): The qcodes.Parameter to validate.

    Raises:
        ValueError: If the parameter is not a qcodes.Parameter, or if its current value is not a float or int.
        ValueError: If the parameter value cannot be retrieved (wrapped).

    Returns:
        Parameter: The original parameter if validation succeeds.
    """
    if not isinstance(parameter, Parameter):
        raise ValueError(f"Invalid parameter type: {type(parameter)}, expected qcodes.Parameter.")

    try:
        value = parameter.get()
        if not isinstance(value, (float, int)):
            raise ValueError(
                f"Invalid parameter value type: {type(value)}, "
                f"expected float or int (Parameter: {parameter.name})."
            )
    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(f"Could not get value from parameter: {parameter.name}") from e

    return parameter
