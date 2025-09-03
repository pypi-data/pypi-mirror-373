from __future__ import annotations

import json
import os
import secrets
import shutil
from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Any

import git
import yaml
from php_framework_detector.core.models import FrameworkType

from php_framework_scaffolder.utils.composer import read_composer_json
from php_framework_scaffolder.utils.docker import run_docker_compose_command
from php_framework_scaffolder.utils.docker import run_docker_compose_command_realtime
from php_framework_scaffolder.utils.logger import get_logger
from php_framework_scaffolder.utils.semver import select_php_version
from php_framework_scaffolder.utils.template import copy_and_replace_template

logger = get_logger(__name__)


class BaseFrameworkSetup(ABC):
    def __init__(self, framework_type: FrameworkType):
        self.framework_type = framework_type
        self.template_dir = Path(f"templates/{framework_type.value}")

    def get_php_version(self, repository_path: Path) -> str:
        composer_data = read_composer_json(
            os.path.join(repository_path, 'composer.json'),
        )
        php_requirement = composer_data.get('require', {}).get('php', '')
        logger.info(f"PHP requirement: {php_requirement}")
        php_version = select_php_version(php_requirement)
        logger.info(f"Selected PHP version: {php_version}")
        return php_version

    def setup(
        self,
        repository_path: Path,
        target_folder: Path,
        apk_packages: list[str] = [],
        php_extensions: list[str] = [],
        pecl_extensions: list[str] = [],
        php_version: str | None = None,
        install_dependencies: bool = True,
        need_clone: bool = True,
        app_port: int = 8000,
        database_type: str = 'mysql',
        database_name: str = 'app',
        database_user: str = 'user',
        database_password: str = secrets.token_hex(8),
        composer_requirements: list[str] = [],
        environment_variables: dict[str, str] = {},
    ) -> None:
        if php_version is None:
            logger.warning('PHP version is not specified')
            php_version = self.get_php_version(repository_path)
        logger.info(f"Using PHP version: {php_version}")

        logger.info(f"Created target folder: {target_folder}")
        self.render_template(
            target_folder=target_folder,
            framework_type=self.framework_type,
            php_version=php_version,
            apk_packages=apk_packages,
            php_extensions=php_extensions,
            pecl_extensions=pecl_extensions,
            install_dependencies=install_dependencies,
            app_port=app_port,
            database_type=database_type,
            database_name=database_name,
            database_user=database_user,
            database_password=database_password,
            composer_requirements=composer_requirements,
            environment_variables=environment_variables,
        )

        if need_clone:
            logger.info(f"Cloning repository to {target_folder / 'src'}")
            git.Repo.clone_from(repository_path, target_folder / 'src')
            logger.info(f"Cloned repository to {target_folder / 'src'}")

        build_command = self.get_docker_build_command()
        logger.info(f"Executing build command: {build_command}")
        run_docker_compose_command_realtime(build_command, target_folder)

        self.shutdown(target_folder)

        up_command = self.get_docker_up_command()
        logger.info(f"Executing up command: {up_command}")
        run_docker_compose_command_realtime(up_command, target_folder)

        setup_commands = self.get_setup_commands()
        logger.info(
            'Starting Docker containers setup',
            total_commands=len(setup_commands),
        )

        for i, command in enumerate(setup_commands, 1):
            logger.info(
                f"Executing setup command {i} of {len(setup_commands)}", command=command,
            )
            run_docker_compose_command_realtime(command, target_folder)

    def render_template(
        self,
        target_folder: Path,
        framework_type: FrameworkType,
        php_version: str,
        apk_packages: list[str],
        php_extensions: list[str],
        pecl_extensions: list[str],
        install_dependencies: bool,
        app_port: int,
        database_type: str,
        database_name: str,
        database_user: str,
        database_password: str,
        composer_requirements: list[str],
        environment_variables: dict[str, str],
    ) -> None:
        """Render templates for a given PHP framework into ``target_folder``.

        This high-level API prepares a sensible default context (APK packages,
        PHP/PECL extensions, ports and DB credentials) and renders the selected
        framework templates into the provided ``target_folder`` using Jinja2.

        Returns the final context used for rendering so callers can persist or
        inspect it if needed.
        """
        merged_apk_packages = [
            'ca-certificates',
            'git',
            'npm',
            'bash',
            'openssl',
            'openssh',
            'linux-headers',
            '$PHPIZE_DEPS',
            'gmp-dev',
            'icu-dev',
            'libffi-dev',
            'libpng-dev',
            'librdkafka-dev',
            'libssh2-dev',
            'libssh2',
            'libxml2-dev',
            'libxslt-dev',
            'libzip-dev',
            'mariadb-client',
            'mysql-client',
            'oniguruma-dev',
            'openldap-dev',
            'postgresql-client',
            'postgresql-dev',
            'zlib-dev',
            'imagemagick-dev',
        ] + apk_packages
        merged_php_extensions = [
            'bcmath',
            'calendar',
            'exif',
            'ffi',
            'ftp',
            'gd',
            'gmp',
            'intl',
            'ldap',
            'pcntl',
            'pdo_mysql',
            'pdo_pgsql',
            'pgsql',
            'soap',
            'sockets',
            'sodium',
            'xsl',
            'zip',
            'mbstring',
            'bz2',
            'opcache',
        ] + php_extensions
        merged_pecl_extensions = [
            'rdkafka',
            'redis',
            'apcu',
            'imagick',
            'xdebug',
        ] + pecl_extensions

        composer_requirements = [
            'dedoc/scramble',
            'knuckleswtf/scribe',
        ] + composer_requirements

        logger.info(f"Using APK packages: {merged_apk_packages}")
        logger.info(f"Using PHP extensions: {merged_php_extensions}")
        logger.info(f"Using PECL extensions: {merged_pecl_extensions}")

        context: dict[str, Any] = {
            'php_version': php_version,
            'app_port': app_port,
            'database_type': database_type,
            'db_database': database_name,
            'db_username': database_user,
            'db_password': database_password,
            'apk_packages': merged_apk_packages,
            'php_extensions': merged_php_extensions,
            'pecl_extensions': merged_pecl_extensions,
            'composer_requirements': composer_requirements,
            'install_dependencies': install_dependencies,
            'environment_variables': environment_variables,
        }

        template_path = Path(os.path.dirname(__file__)).parent / Path(
            f"templates/{str(framework_type)}",
        )
        logger.info(f"Template path: {template_path}")

        logger.info(f"Copying template to {target_folder}")
        copy_and_replace_template(template_path, target_folder, context)
        logger.info(f"Copied template to {target_folder}")

    def _extract_openapi(self, openapi_json_path: Path, target_folder: Path, legacy: bool = False) -> dict[str, Any]:
        if legacy:
            openapi_command = self.get_openapi_command_legacy()
        else:
            openapi_command = self.get_openapi_command()
        logger.info(f"Executing swagger command: {openapi_command}")
        run_docker_compose_command_realtime(openapi_command, target_folder)
        cat_openapi_command = self.get_cat_openapi_command()
        logger.info(f"Executing cat openapi command: {cat_openapi_command}")
        _, openapi_output, _ = run_docker_compose_command(
            cat_openapi_command, target_folder,
        )
        openapi_json = json.loads(openapi_output)
        os.makedirs(openapi_json_path.parent, exist_ok=True)
        with open(openapi_json_path, 'w', encoding='utf-8') as f:
            json.dump(
                openapi_json, f, indent=4,
                ensure_ascii=False, sort_keys=True,
            )
        logger.info(f"OpenAPI JSON saved to {openapi_json_path}")
        return openapi_json

    def extract_openapi(self, openapi_json_path: Path, target_folder: Path) -> dict[str, Any]:
        return self._extract_openapi(
            openapi_json_path, target_folder,
        )

    def extract_openapi_legacy(self, openapi_json_path: Path, target_folder: Path) -> dict[str, Any]:
        return self._extract_openapi(
            openapi_json_path, target_folder,
            legacy=True,
        )

    def get_scramble_command(self) -> list[str]:
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
            'scramble:export',
            '--path', '/app/scramble-openapi.json',
        ]

    def get_cat_scramble_command(self) -> list[str]:
        return [
            'docker',
            'compose',
            'exec',
            '-w',
            '/app',
            'app',
            'cat',
            '/app/scramble-openapi.json',
        ]

    def extract_scramble_openapi(self, openapi_json_path: Path, target_folder: Path) -> dict[str, Any]:
        scramble_command = self.get_scramble_command()
        logger.info(f"Executing scramble command: {scramble_command}")
        run_docker_compose_command_realtime(scramble_command, target_folder)
        cat_scramble_command = self.get_cat_scramble_command()
        logger.info(f"Executing cat scramble command: {cat_scramble_command}")
        _, scramble_output, _ = run_docker_compose_command(
            cat_scramble_command, target_folder,
        )
        openapi_json = json.loads(scramble_output)
        os.makedirs(openapi_json_path.parent, exist_ok=True)
        with open(openapi_json_path, 'w', encoding='utf-8') as f:
            json.dump(
                openapi_json, f, indent=4,
                ensure_ascii=False, sort_keys=True,
            )
        logger.info(f"OpenAPI JSON saved to {openapi_json_path}")
        return openapi_json

    def get_scribe_command(self) -> list[str]:
        return [
            'docker',
            'compose',
            'exec',
            '-w',
            '/app',
            'app',
            'php',
            'artisan',
            'scribe:generate',
        ]

    def get_cat_scribe_private_command(self) -> list[str]:
        return [
            'docker',
            'compose',
            'exec',
            '-w',
            '/app',
            'app',
            'cat',
            '/app/storage/app/private/scribe/openapi.yaml',
        ]

    def get_cat_scribe_public_command(self) -> list[str]:
        return [
            'docker',
            'compose',
            'exec',
            '-w',
            '/app',
            'app',
            'cat',
            '/app/storage/app/public/scribe/openapi.yaml',
        ]

    def extract_scribe(self, openapi_json_path: Path, target_folder: Path) -> dict[str, Any]:
        scribe_command = self.get_scribe_command()
        logger.info(f"Executing scribe command: {scribe_command}")
        run_docker_compose_command_realtime(scribe_command, target_folder)
        for command in [self.get_cat_scribe_private_command(), self.get_cat_scribe_public_command()]:
            try:
                logger.info(f"Executing cat scribe command: {command}")
                _, scribe_output, _ = run_docker_compose_command(
                    command=command, cwd=target_folder,
                )
                openapi_json = yaml.safe_load(scribe_output)
                os.makedirs(openapi_json_path.parent, exist_ok=True)
                with open(openapi_json_path, 'w', encoding='utf-8') as f:
                    json.dump(
                        openapi_json, f, indent=4,
                        ensure_ascii=False, sort_keys=True,
                    )
                logger.info(f"OpenAPI JSON saved to {openapi_json_path}")
                return openapi_json
            except Exception as e:
                logger.error(f"Error executing cat scribe command: {e}")
                continue
        raise Exception('Failed to extract scribe openapi')

    def extract_routes(self, routes_json_path: Path, target_folder: Path) -> dict[str, Any]:
        routes_command = self.get_routes_command()
        logger.info(f"Executing routes command: {routes_command}")
        _, routes_output, _ = run_docker_compose_command(
            routes_command, target_folder,
        )
        routes = json.loads(routes_output)
        logger.info(f"{len(routes)} routes extracted")
        os.makedirs(routes_json_path.parent, exist_ok=True)
        with open(routes_json_path, 'w', encoding='utf-8') as f:
            json.dump(routes, f, indent=4, ensure_ascii=False, sort_keys=True)
        logger.info(f"Routes saved to {routes_json_path}")
        return routes

    def shutdown(self, target_folder: Path) -> None:
        cleanup_command = self.get_docker_down_command(remove_volumes=True)
        logger.info(f"Executing cleanup command: {cleanup_command}")
        run_docker_compose_command_realtime(cleanup_command, target_folder)

    def cleanup(self, target_folder: Path) -> None:
        shutil.rmtree(target_folder)
        logger.info(f"Removed target folder: {target_folder}")

    def get_docker_build_command(self) -> list[str]:
        return [
            'docker',
            'compose',
            'build',
        ]

    def get_docker_up_command(self) -> list[str]:
        return [
            'docker',
            'compose',
            'up',
            '--detach',
            '--wait',
        ]

    def get_docker_down_command(self, remove_volumes: bool = True) -> list[str]:
        return [
            'docker',
            'compose',
            'down',
            '--remove-orphans',
            *(['--volumes'] if remove_volumes else []),
        ]

    @abstractmethod
    def get_setup_commands(self) -> list[list[str]]:
        """
        Get the setup commands for this framework.

        Returns:
            List[List[str]]: A list of command arrays to execute for framework setup
        """

    @abstractmethod
    def get_routes_command(self) -> list[str]:
        """
        Get the command to list routes for this framework.

        Returns:
            List[str]: The command array to execute for listing routes
        """

    def get_openapi_command_legacy(self) -> list[str]:
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
            '/root/.composer-legacy/vendor/bin/openapi',
            '--legacy',
            '--bootstrap', '/app/vendor/autoload.php',
            '--output', '/app/openapi.json',
            '--exclude', 'vendor',
            '--exclude', 'node_modules',
            '--exclude', 'storage',
            '--exclude', 'public',
            '--exclude', 'tests',
            '--format', 'json',
            '/app',
        ]

    def get_openapi_command(self) -> list[str]:
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
            '/root/.composer-modern/vendor/bin/openapi',
            '--bootstrap', '/app/vendor/autoload.php',
            '--output', '/app/openapi.json',
            '--exclude', 'vendor',
            '--exclude', 'node_modules',
            '--exclude', 'storage',
            '--exclude', 'public',
            '--exclude', 'tests',
            '--format', 'json',
            '/app',
        ]

    def get_cat_openapi_command(self) -> list[str]:
        return [
            'docker',
            'compose',
            'exec',
            '-w',
            '/app',
            'app',
            'cat',
            '/app/openapi.json',
        ]
