from __future__ import annotations

from php_framework_detector.core.models import FrameworkType

from php_framework_scaffolder.frameworks.base import BaseFrameworkSetup


class LaravelSetup(BaseFrameworkSetup):
    def __init__(self):
        super().__init__(FrameworkType.LARAVEL)

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
                'artisan',
                'key:generate',
                '--force',
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
                'artisan',
                'migrate',
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
            'artisan',
            'route:list',
            '--json',
            '--no-ansi',
            '--no-interaction',
        ]
