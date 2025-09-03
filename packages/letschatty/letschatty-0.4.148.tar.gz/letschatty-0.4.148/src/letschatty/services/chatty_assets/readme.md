"""
ChattyAsset Class Hierarchy

The system is built around ChattyAssetModel, which provides base functionality for all domain models:

1. ChattyAssetModel
   - Inherits from Pydantic BaseModel
   - Includes UpdateableMixin for immutable updates
   - Includes TimestampValidationMixin for audit fields
   - Core fields: id, name
   - Handles serialization/deserialization

2. ChattyAssetCollectionInterface[T]
   - Generic abstract class for MongoDB operations
   - Type parameter T must be ChattyAssetModel
   - Provides CRUD operations
   - Requires concrete implementation of create_instance()

3. BaseContainer[T]
   - Generic abstract class for in-memory storage
   - Type parameter T must be ChattyAssetModel
   - Manages dictionary of items by ID
   - Basic CRUD operations

4. BaseContainerWithCollection[T]
   - Combines BaseContainer with persistence
   - Uses ChattyAssetCollectionInterface for DB operations
   - Syncs in-memory and DB states
   - Adds features like logical deletion

Usage Flow:
1. Create concrete ChattyAssetModel subclass
2. Implement ChattyAssetCollectionInterface for the model
3. Create container extending BaseContainerWithCollection
4. Use container as single access point for data

Example:
```python
class Source(ChattyAssetModel):
    type: str
    # other fields...

class SourceCollection(ChattyAssetCollectionInterface[Source]):
    def create_instance(self, data: dict) -> Source:
        return SourceFactory.instantiate_source(data)

class SourceContainer(BaseContainerWithCollection[Source]):
    def __init__(self, collection: SourceCollection):
        super().__init__(Source, collection)