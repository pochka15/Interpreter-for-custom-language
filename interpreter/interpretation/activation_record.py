from enum import Enum
from typing import Any, Optional


class ARType(Enum):
    START = 'START',
    FUNCTION = 'FUNCTION'


class ActivationRecord:
    def __init__(self, name: str, record_type: ARType, nesting_level: int):
        self.name: str = name
        self.type: ARType = record_type
        self.nesting_level: int = nesting_level
        self.members = {}

    def __setitem__(self, key, value):
        self.members[key] = value

    def __getitem__(self, key):
        return self.members[key]

    def get(self, key) -> Optional[Any]:
        """get the activation record member by the key"""
        return self.members.get(key)

    def __str__(self):
        lines = [
            '{level}: {type} {name}'.format(
                level=self.nesting_level,
                type=self.type.value,
                name=self.name,
            )
        ]
        for name, val in self.members.items():
            lines.append(f'   {name:<20}: {val}')

        s = '\n'.join(lines)
        return s
