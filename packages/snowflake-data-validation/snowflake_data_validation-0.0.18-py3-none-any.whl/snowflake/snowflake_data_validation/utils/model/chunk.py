from dataclasses import dataclass


@dataclass
class Chunk:

    """Represents a chunk of data to be processed.

    Attributes:
        fetch (int): The number of records to fetch in this chunk.
        offset (int): The starting point from which to fetch the records.

    """

    fetch: int
    offset: int
