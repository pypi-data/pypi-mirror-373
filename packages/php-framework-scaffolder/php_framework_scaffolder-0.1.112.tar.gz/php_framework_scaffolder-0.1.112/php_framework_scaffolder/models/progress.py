from __future__ import annotations

from enum import Enum


class ImplementationProgress(Enum):
    TODO = 'todo'
    WIP = 'wip'
    DONE = 'done'

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)
