from __future__ import annotations

from php_framework_detector.core.models import FrameworkType

from php_framework_scaffolder.frameworks.base import BaseFrameworkSetup


class YiiSetup(BaseFrameworkSetup):
    def __init__(self):
        super().__init__(FrameworkType.YII)

    def get_setup_commands(self) -> list[list[str]]:
        return [
            [
                'docker',
                'compose',
                'exec',
                '-w',
                '/app',
                'app',
                'php',
                'yii',
                'migrate',
                '--interactive=0',
                '--no-interaction',
                '--no-ansi',
            ],
        ]

    def get_routes_command(self) -> list[str]:
        raise NotImplementedError('Not implemented')
