from abc import ABCMeta
from typing import Any, Dict, List, Callable
import inspect
from inspect import Parameter, Signature
from collections import defaultdict
import copy

# Replace these imports with your actual module paths
from .weavitae_reference import Reference
from .weaviate_property import Property
from .weaviate_utility import validate_method_params

from weaviate.classes.config import (
    Property as WeaviateProperty,
    ReferenceProperty as WeaviateReferenceProperty,
    Configure
)

from weaviate.collections.collections.sync import _Collections

from abc import ABCMeta
from typing import Any, Dict, List, Callable
import inspect
from inspect import Parameter, Signature
from collections import defaultdict
import copy

from .weavitae_reference import Reference
from .weaviate_property import Property
from .weaviate_utility import validate_method_params
from weaviate.classes.config import Configure
from weaviate.collections.collections.sync import _Collections


class Weaviate_Meta(ABCMeta):
    _weaviate_schema: dict[str, Any]
    _properties: list[Property]
    _references: list[Reference]
    _abstract : bool = True  # This is an abstract class set to False in all subclasses. If abstract is True, the class cannot created in Weaviate.

    """
    Metaclass that dynamically extracts model attributes to build Weaviate schemas.

    - If an attribute is an instance of `Property`, we treat it as a scalar property.
    - If it's a `Reference`, we treat it as a cross-reference property.
    - If a class variable `__collection_name__` is present, we use that name
      as the Weaviate class name instead of the Python class name.

    We also look for specific config attribute names (like "vectorizer_config")
    to store in the final schema dict.
    """

    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)

        properties: List[Property] = []
        references: List[Reference] = []

        # --- merge callback registries from bases (as before) ---
        merged: Dict[str, List[Callable]] = defaultdict(list)
        for base in bases:
            for ev, fns in getattr(base, "_callbacks", {}).items():
                for fn in fns:
                    if fn not in merged[ev]:
                        merged[ev].append(fn)
        setattr(cls, "_callbacks", dict(merged))

        if name != "Base_Model":
            collection_name = dct.get("__collection_name__", name)
            weaviate_collection = {
                "name": collection_name,
                "description": dct.get("description", ""),
                "properties": [],
                "references": [],
                "vectorizer_config": Configure.Vectorizer.none(),
                "vector_index_config": None,
                "inverted_index_config": None,
                "generative_config": None,
            }

            # 1) add properties/references defined *on this class body*
            for attr_name, attr_value in cls.__dict__.items():
                if isinstance(attr_value, Property):
                    weaviate_collection["properties"].append(
                        attr_value._get_weaviate_property()
                    )
                    properties.append(attr_value)
                elif isinstance(attr_value, Reference):
                    weaviate_collection["references"].append(
                        attr_value._get_weaviate_reference()
                    )
                    references.append(attr_value)

            # 2) inherit from bases: deep‑copy and *rebind* onto subclass if missing here
            for base in bases:
                for base_prop in getattr(base, "_properties", []):
                    if base_prop.name and base_prop.name not in cls.__dict__:
                        prop_copy = copy.deepcopy(base_prop)
                        prop_copy.inherited = True
                        setattr(cls, base_prop.name, prop_copy)
                        # ensure descriptor binding now that we set it dynamically
                        if hasattr(prop_copy, "__set_name__"):
                            prop_copy.__set_name__(cls, base_prop.name)

                        weaviate_collection["properties"].append(
                            prop_copy._get_weaviate_property()
                        )
                        properties.append(prop_copy)

                for base_ref in getattr(base, "_references", []):
                    if base_ref.name and base_ref.name not in cls.__dict__:
                        ref_copy = copy.deepcopy(base_ref)
                        ref_copy.inherited = True
                        setattr(cls, base_ref.name, ref_copy)
                        if hasattr(ref_copy, "__set_name__"):
                            ref_copy.__set_name__(cls, base_ref.name)

                        weaviate_collection["references"].append(
                            ref_copy._get_weaviate_reference()
                        )
                        references.append(ref_copy)

            # 3) apply collection-level configs from class attributes if provided
            for key in (
                "vectorizer_config",
                "vector_index_config",
                "inverted_index_config",
                "generative_config",
            ):
                val = getattr(cls, key, None)
                if val is not None:
                    weaviate_collection[key] = val

            # 4) validate and attach schema, registries and dynamic __init__
            validate_method_params(_Collections.create, weaviate_collection)

            # Set abstract property of class
            if "_abstract" in dct:
                cls._abstract = dct["_abstract"]
            else:
                cls._abstract = False

            cls._weaviate_schema = weaviate_collection
            cls._properties = properties
            cls._references = references

            if "__init__" not in dct:
                cls.__init__ = mcs._make_dynamic_init(properties=properties, references=references)

        return cls
    
    @staticmethod
    def _make_dynamic_init(properties:list[Property], references:list[Reference]): #TODO: Rewrite this function!!!
        """
        Build a function with a dynamic signature for __init__.
        Each `Property` or `Reference` becomes a keyword parameter (with default if any).
        """
        # We'll build an inspect.Signature that has parameters for each property/ref.
        parameters = []

        # 0) Add the `self` parameter
        #parameters.append(
        #    Parameter(
        #        name="self",
        #        kind=Parameter.POSITIONAL_ONLY
        #    )
        #)

        # 1) Create parameters for each Property
        for prop in properties:
            # If the property has a default, use that; otherwise Parameter.empty
            default_val = prop.default if (prop.default is not None) else Parameter.empty
            kind = Parameter.POSITIONAL_OR_KEYWORD

            if not prop.name:
                raise ValueError("Property name is not set.")

            parameters.append(
                Parameter(
                    name=prop.name,
                    kind=kind,
                    default=default_val,
                    annotation=prop.cast_type
                )
            )

        # 2) Create parameters for each Reference
        for ref in references:
            # Typically references won't have "default" in the same sense, but if you do:
            default_val = None if not ref.required else Parameter.empty

            if not ref.name:
                raise ValueError("Reference field name is not set.")
            
            parameters.append(
                Parameter(
                    name=ref.name,
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    default=default_val,
                    annotation=ref.target_collection_name  # Get type from the target collection name -> str to type
                )
            )

        # Build a signature with the above parameters
        sig = Signature(parameters=parameters)

        # Now define the actual function that uses that signature at runtime.
        def dynamic_init(self, *args, **kwargs):
            # Bind arguments to the signature -> enforces correct usage
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # bound_args.arguments is an OrderedDict of (param_name -> value)
            # first argument is `self`, skip it when setting attributes
            for param_name, arg_val in list(bound_args.arguments.items()):
                if(param_name in self.__dict__):
                    raise ValueError(f"Parameter '{param_name}' already exists in the class.")
                setattr(self, param_name, arg_val)

            #Set uuid
            self.generate_uuid()

        # Attach our custom signature to the function object
        dynamic_init.__signature__ = sig
        # For better debugging, give it a nice name:
        dynamic_init.__name__ = "__init__"

        return dynamic_init
