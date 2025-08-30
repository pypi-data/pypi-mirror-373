# Weaviate ORM
### A Pythonic ORM-style layer for Weaviate

`weaviate-orm` provides a structured, object-oriented interface to the Weaviate vector database. Inspired by traditional ORM patterns, it allows you to define collections as Python classes, automatically generate Weaviate schemas, and perform CRUD and similarity-based queries without leaving the object-oriented paradigm.

## Features

- **Declarative Schema Definition**  
  Define collections using Python classes and descriptors for properties and cross-references.

- **Dynamic Schema Generation via Metaclass**  
  A metaclass extracts property and reference definitions to auto-generate Weaviate-compatible schema structures.

- **Object-Oriented CRUD Operations**  
  Seamlessly create, retrieve, update, and delete data using instance methods — no raw queries needed.

- **Recursive Save & Update**  
  Handles deeply nested references and automatically saves or updates related objects when desired.

- **Flexible Engine Binding**  
  The engine takes any connection method from the `weaviate` library, allowing support for local, remote, or custom configurations.

- **UUID Management**  
  Built-in support for both `uuid4` and `uuid5` strategies — including UUID validation and immutability enforcement.

- **Optional Auto-loading of References**  
  Cross-references can be automatically resolved into full model instances when accessed.

- **Support for Near-Vector and Near-Text Queries**  
  Leverage Weaviate’s native similarity search APIs directly from your model classes.

- **Strict Typing and Validation**  
  Type enforcement and optional validation logic on properties and references using Python descriptors.

- **Fully Tested**  
  Includes both unit and integration tests with Pytest and Docker-based Weaviate setups.

---

## Design Patterns

- **Descriptor Pattern**  
  Custom `Property` and `Reference` descriptors manage validation, casting, and schema representation of scalar and relational fields.

- **Metaclass-Based Schema Introspection**  
  A metaclass (`Weaviate_Meta`) dynamically collects all descriptors from a class and builds the full Weaviate schema. It also generates a dynamic `__init__` constructor based on the field signatures.

- **Engine Abstraction Layer**  
  The `Weaviate_Engine` encapsulates connection logic and schema management. It supports any connection method compatible with the `weaviate` Python client (e.g., local, remote, or cloud).

- **Instance-Oriented CRUD**  
  CRUD operations (including recursive reference handling and UUID safety checks) are exposed as instance methods on models that inherit from `Base_Model`.

- **Reference Resolution Strategy**  
  `Reference` descriptors can be configured to auto-load full objects (not just UUIDs), and support both one-way and two-way references, as well as single or list cardinalities.

---

## Installation

You can install `weaviate_orm` either from PyPI (once published) or directly from the source repository.

### 📦 From PyPI (recommended)
```bash
pip install weaviate-orm
```

### 🛠 From Git (development and testing)
```bash
git clone https://gitlab.opencode.de/bbsr_ida_public/weaviate_orm.git
cd weaviate_orm
pip install -e .
```
Note: Make sure your Python environment includes the required Weaviate client:

```bash
pip install weaviate-client
```

## Quick Start
In this example, we will use a local Weaviate instance using text2vec_ollama as the default vectorizer with a local ollama instance running and providing "snowflake-arctic-embed2" as embedding model.

### Create a Model
Create two related models `Paper` and `Author` and specify configuration for the weaviate schema. 

```python
from __future__ import annotations

import os
from uuid import UUID, uuid5
import datetime

from weaviate_orm.weaviate_base import Base_Model
from weaviate_orm.weaviate_property import Property
from weaviate_orm.weavitae_reference import Reference, Reference_Type

from weaviate.classes.config import Configure, DataType

# Get the host and port from environment variables
llm_host = os.getenv("LLM_HOST", "llm")
llm_port = int(os.getenv("LLM_PORT", 11434))

class Paper(Base_Model):
    vectorizer_config = Configure.Vectorizer.text2vec_ollama(    
            api_endpoint = f"http://{llm_host}:{llm_port}", #api-endpoint for the local ollama model
            model = "snowflake-arctic-embed2", #Embedding model to use
            vectorize_collection_name = False
        )
    
    title = Property(cast_type=str, description="The title of the paper", required=True, weaviate_type=DataType.TEXT, vectorize_property_name=True)
    abstract = Property(cast_type=str, description="The abstract of the paper", required=True, weaviate_type=DataType.TEXT, vectorize_property_name=True)
    pub_date = Property(cast_type=datetime.date, description="The publication date of the paper", required=True, weaviate_type=DataType.DATE, skip_vectorization=True)
    doi = Property(cast_type=str, description="The doi of the paper", required=True, weaviate_type=DataType.TEXT, skip_vectorization=True)
    author = Reference(target_collection_name="Author", auto_loading=True, description="The author of the paper", reference_type=Reference_Type.SINGLE, way_type=Reference_Type.TWOWAY, required=False, skip_validation=True)
    co_authors = Reference(target_collection_name="Author", auto_loading=False, description="The co-authors of the paper", reference_type=Reference_Type.LIST, way_type=Reference_Type.ONEWAY, required=False, skip_validation=True)

    _namespace = UUID("eb8bc242-5f59-4a47-8230-0cea6fcc1028")

    def _get_uuid_name_string(self):
        return self.doi
        
class Author(Base_Model):
    first_name = Property(cast_type=str, description="The first name of the author", required=True, weaviate_type=DataType.TEXT, vectorize_property_name=True)
    last_name = Property(cast_type=str, description="The last name of the author", required=True, weaviate_type=DataType.TEXT, vectorize_property_name=True)
    orc_id = Property(cast_type=str, description="The orc_id of the author", required=False, weaviate_type=DataType.TEXT, skip_vectorization=True)
    papers = Reference(target_collection_name="Paper", auto_loading=False, description="The papers of the author", reference_type=Reference_Type.LIST, way_type=Reference_Type.TWOWAY, required=False, skip_validation=True)

    _namespace = UUID("eb8bc242-5f59-4a47-8230-0cea6fcc1028")

    def _get_uuid_name_string(self) -> str:
        return f"{self.first_name} {self.last_name}"

```

### Create a Weaviate Engine, Register Models, and Create Schema

```python
from weaviate_orm.weaviate_engine import Weaviate_Engine
from weaviate import connect_to_local, connect_to_weaviate_cloud

# Get host and ports from environment variables
host = os.getenv("WEAVIATE_HOST", "vdatabase")
port = int(os.getenv("WEAVIATE_PORT", 8080))
grpc_port = int(os.getenv("WEAVIATE_GRPC_PORT", 50051))

# Initialize the Weaviate engine using the connect_to_local method and its parameters
engine = Weaviate_Engine(connect_to_local, host=host, port=port, grpc_port=grpc_port)

# Register the models with the engine
engine.register_all_models(Paper, Author)

# Create the schema in Weaviate
engine.create_all_schemas()
```

### Create and Save Instances

```python
# Example data
paper_data = {
    "title": "A Study on Weaviate ORM",
    "abstract": "This paper discusses the Weaviate ORM and its features.",
    "pub_date": datetime.datetime.now(datetime.timezone.utc),
    "doi": "10.1234/weaviate-orm",
}

author_data = {
    "first_name": "Allen",
    "last_name": "Turing",
    "orc_id": "0000-0002-1234-5678",
}

# Create an insance of author and paper

author = Author(first_name=author_data["first_name"],
                last_name=author_data["last_name"],
                orc_id=author_data["orc_id"])

paper = Paper(title=paper_data["title"],
                abstract=paper_data["abstract"],
                pub_date=paper_data["pub_date"],
                doi=paper_data["doi"],
                author=author)

# Save the author and paper to Weaviate
paper.save(include_references=True, recursive=True)
```

### Read an Instance
```python 
# Retrieve the paper by its UUID
paper_uuid = paper.get_uuid()

paper_instance = Paper.get(paper_uuid, include_references=True)
print(f"Paper Title: {paper_instance.title}")
print(f"Author: {paper_instance.author.first_name} {paper_instance.author.last_name}")
```

### Update an Instance
```python
# Update the paper's title
paper_instance.title = "An Updated Study on Weaviate ORM"
paper_instance.update()

#Check updated instance
paper_instance = Paper.get(paper_uuid, include_references=True)
print(f"Paper Title: {paper_instance.title}")
```

### Delete an Instance
```python
# Delete the paper instance
paper_instance.delete()
```

## Project Structure
```
weaviate_orm/
│
├── __init__.py              # Public interface and versioning
├── weaviate_base.py         # Base_Model with full CRUD logic and query support
├── weaviate_engine.py       # Manages Weaviate client and schema creation
├── weaviate_meta.py         # Metaclass for schema extraction and dynamic __init__
├── weaviate_property.py     # Descriptor for scalar fields
├── weavitae_reference.py    # Descriptor for references (one-way, two-way, single, list)
├── weaviate_decorators.py   # Client injection and async-to-sync conversion
└──  weaviate_utility.py      # Helpers for validation and reference comparison
```

## License
This project is licensed under the GNU General Public License v3.0 (GPLv3).

You are free to use, modify, and distribute this software under the terms of the GPLv3 license. Any derivative work must also be distributed under the same license.

For full details, see the [LICENSE](https://choosealicense.com/licenses/gpl-3.0/).

## Contributing & Credits
This project is created and maintained by the BBSR - IDA (Tobias Heimig-Elschner).
Feel free to open issues or submit pull requests if you encounter bugs, have ideas, or want to improve the package.

### 📚 Citation
The project is published on Zenodo and can be cited as:
Heimig, T. (2025). Weaviate ORM - (0.1.0). Bundesinstitut für Bau-, Stadt- und Raumforschung (BBSR). https://doi.org/10.58007/x1wa-rt92

## Roadmap & Open Development Topics
- **Batch Operations**<br>Add support for batched inserts and updates for high-throughput use cases.

- **Generalized Query Interface**<br>Unify near-vector, near-text, and filter queries into a common, fluent interface.

- **Nested Reference Updates**<br>Extend update logic to fully support reference deletions and new nested reference creation during .update() calls.