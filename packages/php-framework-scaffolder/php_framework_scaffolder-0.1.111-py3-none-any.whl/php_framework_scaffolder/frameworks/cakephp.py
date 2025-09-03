from __future__ import annotations

from php_framework_detector.core.models import FrameworkType

from php_framework_scaffolder.frameworks.base import BaseFrameworkSetup


class CakePHPSetup(BaseFrameworkSetup):
    def __init__(self):
        super().__init__(FrameworkType.CAKEPHP)

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
                'bin/cake.php',
                'migrations',
                'migrate',
                '--no-interaction',
                '--no-ansi',
            ],
        ]

    def get_routes_command(self) -> list[str]:
        return [
            'docker',
            'compose',
            'exec',
            '-w',
            '/app',
            'app',
            'php',
            'bin/cake.php',
            'routes',
        ]
