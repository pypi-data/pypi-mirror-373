from dataclasses import dataclass


@dataclass
class VectorCollectionMetadata:
    collection_name: str
    last_updated: str
    last_queried: str
    query_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> 'VectorCollectionMetadata':
        """Create an instance from a dictionary."""
        return cls(
            collection_name=data.get('collection_name', ''),
            last_updated=data.get('last_updated', ''),
            last_queried=data.get('last_queried', ''),
            query_count=data.get('query_count', 0)
        )

    def to_dict(self) -> dict:
        """Convert instance to a dictionary."""
        return {
            'collection_name': self.collection_name,
            'last_updated': self.last_updated,
            'last_queried': self.last_queried,
            'query_count': self.query_count
        }


