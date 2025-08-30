from typing import Callable, Awaitable, Dict, Set
from dataclasses import dataclass


@dataclass
class Transformer:
    """Data model for a transformer"""

    name: str
    """name of the transformer"""

    transformer: Callable[[Dict], Awaitable[Dict]]
    """method that transforms the data"""

    inputs: Set[str]
    """list of required input fields"""

    outputs: Set[str]
    """list of output fields"""

    def __hash__(self):
        return hash(self.name)
