from __future__ import annotations
from typing import Callable, Type, Optional, Union, List, TYPE_CHECKING, Any
from uuid import UUID

from weaviate.classes.config import DataType, Property as weaviateProperty, Tokenization, ReferenceProperty as weaviateReferenceProperty
from weaviate.collections import Collection
from weaviate.util import _WeaviateUUIDInt
if TYPE_CHECKING:
    from .weaviate_base import Base_Model

class Reference_Type:
    
    """
    Enum of the possible reference types.

    Attributes:
        SINGLE: A single reference.
        MULTIPLE: A list of references.
    """

    ONEWAY = "oneway"
    TWOWAY = "twoway"

    SINGLE = "single"
    LIST = "list"


class Reference:

    """
    Declares a reference field to another Weaviate class/collection.

    Attributes:
        target_collection (Base_Model): The target Weaviate collection.
        description (str): A human-readable description of the reference field.
        required (bool): Whether the reference field is required.
        auto_loading (bool): Whether to automatically load the referenced entity when accessed.
    """

    def __init__(self, target_collection_name:str, description:str, way_type:str=Reference_Type.ONEWAY, reference_type=Reference_Type.SINGLE, required:bool=False, auto_loading:bool=False, skip_validation:bool=False, inherited:bool=False):
        """
        Initialize the reference field descriptor.

        Args:
            target_collection (str): Name of the target_collection.
            description (str): A human-readable description of the reference field.
            required (bool, optional): Whether the reference field is required. Defaults to False.
            auto_loading (bool, optional): Whether to automatically load the referenced entity when accessed. Defaults to False. If false, the field will return the UUID of the referenced entity.
            way_type (str, optional): The way type of the reference. Defaults to Reference_Type.ONEWAY.
            reference_type (str, optional): The type of the reference. Defaults to Reference_Type.SINGLE. Can be Reference_Type.SINGLE or Reference_Type.LIST.
            skip_validation (bool, optional): Whether to skip validation of the reference field. Defaults to False.
            inherited (bool, optional): Whether the reference is inherited from a parent class. Defaults to False.
        """

        # Ensure we got a subclass of Base_Model
        #try:
        #    from .weaviate_base import Base_Model  # for runtime check
        #    if not issubclass(target_collection, Base_Model):
        #        raise TypeError(f"target_collection must be a subclass of Base_Model, got {target_collection!r}")
        #except ImportError:
        #    # If there's a circular issue, you might do a fallback or rely on the TYPE_CHECKING block
        #    pass

        self.target_collection_name = target_collection_name
        self.description = description
        self.required = required
        self.auto_loading = auto_loading
        self.way_type = way_type
        self.reference_type = reference_type
        self.skip_validation = skip_validation
        self.inherited = inherited

        self.name: Optional[str] = None  # Assigned by __set_name__

    def __set_name__(self, owner, name):
        """
        Called automatically when the descriptor is assigned to a class attribute.
        """
         
        self.name = name
        self._owner = owner

    def __get__(self, instance, owner):

        """
        Access the value stored on the instance. If accessed from the class (instance is None)

        Args:
            instance: The instance of the class.
            owner: The class itself.

        Returns:
            Union[Base_Model, UUID]: The referenced entity or its UUID.

        Raises:
            ValueError: If the reference field is required but not set.
        """

        # If accessed on the class itself, return the descriptor instance
        if instance is None:
            return self
        
        val = instance.__dict__.get(self.name)

        # If not set
        if val is None:
            if self.required:
                raise ValueError(f"Reference field '{self.name}' is required but not set.")
            return None
        
        # If set, handle the value
        value = self._handling_lists(instance, val)

        return value

    def __set__(self, instance, value):
        """
        Handle writing to the reference field: optional validation and loading the referenced entity.

        Args:
            instance: The instance of the class.
            value: The value to set.

        Raises:
            ValueError: If the field is set with an invalid value.
        """

        value = self._handling_lists(instance, value)
        
        # Validate the value
        if not self._validate(value):
            raise ValueError(f"Invalid value ({value}) for reference field '{self.name}'")

        # Store the final value in the instance
        instance.__dict__[self.name] = value

    def _get_target_collection(self, owner) -> Collection:
        """
        Get the target collection from weaviate.

        Args:
            owner: The class that owns the reference field.

        Returns:
            Collection: The target collection.
        """

        collection = None

        with owner._engine.client as client:
            collection = client.collections.get(self.target_collection_name)

        return collection
    
    def _get_target_class(self) -> Type['Base_Model']:

        target_class = None
        collection_classes =  {model.__name__ : model for model in self._owner._engine._models}

        if self.target_collection_name in collection_classes:
            target_class = collection_classes[self.target_collection_name]
        
        else:
            raise ValueError(f"Target class '{self.target_collection_name}' not found in the engine. Do you have a model for it?")
        
        return target_class

    def _validate(self, value) -> bool:
        """
        Validate the value of the reference field. If not required, None is allowed.

        Args:
            value: The value to validate.

        Returns:
            bool: True if the value is valid, False otherwise

        Raises:
            ValueError: If the value is invalid.
        """

        if self.skip_validation:
            return True

        # None is okay if not required
        if value is None:
            if self.required:
                raise ValueError(f"Reference field '{self.name}' is required, but got None.")
            
            return True
        
        target_class = self._get_target_class()

        # Otherwise, must be either a UUID or a target_collection instance
        if self.reference_type==Reference_Type.SINGLE and (not (isinstance(value, UUID) or isinstance(value, target_class))):
            print(f"DEBUG: {value} is not a UUID or instance of {target_class}")
            return False
        elif self.reference_type == Reference_Type.LIST and (not isinstance(value, list) or not all(isinstance(v, target_class) for v in value)):
            print(f"DEBUG: {value} is not a list of instances of {target_class}")
            return False

        # If it's a target_collection instance, ensure it's valid #TODO: Implement is_valid in Base_Model
        # (UUIDs are always considered valid)
        if isinstance(value, UUID):
            return True
        elif isinstance(value, list) and all(isinstance(v, target_class) for v in value) and all(v.is_valid for v in value):
            return True
        elif isinstance(value, target_class) and hasattr(value, 'is_valid') and not value.is_valid:
            print(f"DEBUG: {value} is not valid")
            return False
        
        return True
        
    def _get_weaviate_reference(self) -> weaviateReferenceProperty:

        """
        Get the Weaviate reference property configuration.

        Returns:
            weaviateReferenceProperty: The Weaviate reference property configuration.

        Raises:
            ValueError: If the reference field name is not set.
        """

        if self.name is None:
            raise ValueError("Reference field name is not set; cannot create Weaviate reference property from not assigned reference field")
        
        ref = weaviateReferenceProperty(
            name=self.name,
            description=self.description,
            target_collection=self.target_collection_name,
        )

        return ref

    def _handle_weaviate_uuid(self, input_value) -> Union[UUID, Any]:
        """
        Handle the Weaviate UUID type. Convert it to a UUID object. If value is not a _WeaviateUUIDInt, return it as is.

        Args:
            value: The value to handle.

        Returns:
            Union[UUID, Any]: The handled value.
        """

        if isinstance(input_value, _WeaviateUUIDInt):
            input_value = UUID(str(input_value.hex))
        
        return input_value

    def _handle_auto_loading(self, input_value, target_class=None) -> Union[UUID, Any]:
        """
        Handle the auto_loading of the reference field.

        Args:
            input_value: The value to handle.
            target_class (Optional): The target class to load the reference from. Defaults to None - Reference._get_target_class() is used.

        Returns:
            Union[UUID, Any]: The handled value. Value of type target_class if auto_loading is True, otherwise the UUID.        
        """

        # Handle UUID
        value = self._handle_weaviate_uuid(input_value)

        # Handle target_class
        if target_class is None and self.auto_loading:
            target_class = self._get_target_class()

        if isinstance(value, UUID) and self.auto_loading:
            # Fetch the referenced object
            if target_class is None:
                raise ValueError("Target class is not set; cannot auto-load the reference.")
            
            value = target_class.get(value)

        return value

    def _handling_lists(self, instance, input_value):
        """
        Handle the input value for the reference field. If the reference type is SINGLE, ensure that only a single value is set.
        If the reference type is LIST, ensure that a list of values is set.

        Args:
            instance: The instance of the class.
            input_value: The value to handle.

        Raises:
            ValueError: If the reference field is a single reference but multiple values are provided.
        """

        if isinstance(input_value, list) and self.reference_type == Reference_Type.SINGLE:
            if len(input_value) > 1:
                raise ValueError(f"Reference field '{self.name}' is a single reference but got multiple values: {input_value}")
            elif len(input_value) == 1 and input_value[0] is not None:
                value = input_value[0]
            elif len(input_value) == 1 and input_value[0] is None:
                value = None
            elif len(input_value) == 0:
                value = None
        else:
            value = input_value

        #Provide target_class for auto_loading
        target_class = None
        if self.auto_loading:
            target_class = self._get_target_class()

        if value == [] or value is None:
            value = None

        elif isinstance(value, list):
            # Handle the list of references
            for i, v in enumerate(value):
                # Handle UUID and auto_loading
                value[i] = self._handle_auto_loading(v, target_class=target_class)
        else:
            # Handle single reference
            value = self._handle_auto_loading(value, target_class=target_class)

        return value
    
