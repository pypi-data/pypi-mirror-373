from dataclasses import dataclass


@dataclass
class VectorQueryAnswer:
    text: str
    dimension: str

    @classmethod
    def from_dict(cls, data: dict) -> 'VectorQueryAnswer':
        """Create an instance from a dictionary."""
        return cls(
            text=data.get('text', ''),
            dimension=data.get('dimension', ''),
        )

    def to_dict(self) -> dict:
        """Convert instance to a dictionary."""
        return {
            'text': self.text,
            'dimension': self.dimension,
        }