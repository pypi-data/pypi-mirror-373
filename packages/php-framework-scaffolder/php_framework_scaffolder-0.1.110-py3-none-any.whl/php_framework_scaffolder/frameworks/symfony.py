from __future__ import annotations

from php_framework_detector.core.models import FrameworkType

from php_framework_scaffolder.frameworks.base import BaseFrameworkSetup


class SymfonySetup(BaseFrameworkSetup):
    def __init__(self):
        super().__init__(FrameworkType.SYMFONY)

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
                'bin/console',
                'cache:clear',
                '--no-interaction',
                '--no-ansi',
            ],
            [
                'docker',
                'compose',
                'exec',
                '-w',
                '/app',
                'app',
                'php',
                'bin/console',
                'doctrine:database:create',
                '--if-not-exists',
                '--no-interaction',
                '--no-ansi',
            ],
            [
                'docker',
                'compose',
                'exec',
                '-w',
                '/app',
                'app',
                'php',
                'bin/console',
                'doctrine:schema:update',
                '--force',
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
            '-d',
            'error_reporting=~E_DEPRECATED',
            'bin/console',
            'debug:router',
            '--format=json',
            '--no-interaction',
            '--no-ansi',
        ]
