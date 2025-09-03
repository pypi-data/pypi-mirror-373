from __future__ import annotations

from php_framework_detector.core.models import FrameworkType

from php_framework_scaffolder.frameworks.base import BaseFrameworkSetup


class NaSetup(BaseFrameworkSetup):
    def __init__(self):
        super().__init__(FrameworkType.NA)

    def get_setup_commands(self) -> list[list[str]]:
        raise NotImplementedError('Not implemented')

    def get_routes_command(self) -> list[str]:
        raise NotImplementedError('Not implemented')
