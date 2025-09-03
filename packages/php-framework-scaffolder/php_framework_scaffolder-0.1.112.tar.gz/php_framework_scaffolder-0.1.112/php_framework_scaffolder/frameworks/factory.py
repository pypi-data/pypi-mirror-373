from __future__ import annotations

import structlog
from php_framework_detector.core.models import FrameworkType

from php_framework_scaffolder.frameworks.base import BaseFrameworkSetup
from php_framework_scaffolder.frameworks.cakephp import CakePHPSetup
from php_framework_scaffolder.frameworks.codeigniter import CodeIgniterSetup
from php_framework_scaffolder.frameworks.drupal import DrupalSetup
from php_framework_scaffolder.frameworks.drush import DrushSetup
from php_framework_scaffolder.frameworks.fastroute import FastRouteSetup
from php_framework_scaffolder.frameworks.fatfree import FatFreeSetup
from php_framework_scaffolder.frameworks.fuel import FuelSetup
from php_framework_scaffolder.frameworks.laminas import LaminasSetup
from php_framework_scaffolder.frameworks.laravel import LaravelSetup
from php_framework_scaffolder.frameworks.phalcon import PhalconSetup
from php_framework_scaffolder.frameworks.phpixie import PhPixieSetup
from php_framework_scaffolder.frameworks.popphp import PopPHPSetup
from php_framework_scaffolder.frameworks.slim import SlimSetup
from php_framework_scaffolder.frameworks.symfony import SymfonySetup
from php_framework_scaffolder.frameworks.thinkphp import ThinkPHPSetup
from php_framework_scaffolder.frameworks.yii import YiiSetup
from php_framework_scaffolder.frameworks.zendframework import ZendFrameworkSetup

logger = structlog.get_logger(__name__)


def _is_framework_implemented(framework_class_type) -> bool:
    """
    Check if a framework is actually implemented by testing if it can be instantiated
    (i.e., all abstract methods are implemented).
    """
    try:
        # Try to instantiate the class - this will fail if abstract methods are not implemented
        instance = framework_class_type()
        # Try to call get_setup_commands to see if it's properly implemented
        setup_commands = instance.get_setup_commands()
        return isinstance(setup_commands, list) and len(setup_commands) > 0
    except TypeError as e:
        # This happens when abstract methods are not implemented
        if 'abstract' in str(e).lower():
            return False
        logger.error(f"TypeError checking if framework is implemented: {e}")
        return False
    except NotImplementedError:
        # Some frameworks might still use the old pattern
        return False
    except Exception as e:
        logger.error(f"Error checking if framework is implemented: {e}")
        return False


def _get_available_frameworks():
    """
    Dynamically discover which frameworks are actually implemented.
    """
    all_framework_classes = {
        FrameworkType.LARAVEL: LaravelSetup,
        FrameworkType.SYMFONY: SymfonySetup,
        FrameworkType.CODEIGNITER: CodeIgniterSetup,
        FrameworkType.CAKEPHP: CakePHPSetup,
        FrameworkType.YII: YiiSetup,
        FrameworkType.THINKPHP: ThinkPHPSetup,
        FrameworkType.SLIM: SlimSetup,
        FrameworkType.FATFREE: FatFreeSetup,
        FrameworkType.FASTROUTE: FastRouteSetup,
        FrameworkType.FUEL: FuelSetup,
        FrameworkType.PHALCON: PhalconSetup,
        FrameworkType.PHPIXIE: PhPixieSetup,
        FrameworkType.POPPHP: PopPHPSetup,
        FrameworkType.LAMINAS: LaminasSetup,
        FrameworkType.ZENDFRAMEWORK: ZendFrameworkSetup,
        FrameworkType.DRUPAL: DrupalSetup,
        FrameworkType.DRUSH: DrushSetup,
    }

    # Filter out unimplemented frameworks and create instances
    implemented_frameworks = {}
    for framework_type, framework_class in all_framework_classes.items():
        if _is_framework_implemented(framework_class):
            implemented_frameworks[framework_type] = framework_class()

    return implemented_frameworks


# Cache the available frameworks to avoid repeated checks
_AVAILABLE_FRAMEWORKS = None


def get_framework_handler(framework: FrameworkType) -> BaseFrameworkSetup:
    """
    Get a framework handler for the specified framework type.
    Only returns handlers for frameworks that are actually implemented.

    Args:
        framework: The framework type to get a handler for

    Returns:
        BaseFrameworkSetup: The framework handler instance

    Raises:
        ValueError: If the framework type is invalid or None
        NotImplementedError: If the framework is valid but not implemented yet
    """
    global _AVAILABLE_FRAMEWORKS

    # Check if framework is None or invalid
    if framework is None:
        raise ValueError('Framework type cannot be None')

    if not isinstance(framework, FrameworkType):
        raise ValueError(
            f"Invalid framework type: {framework}. Must be a FrameworkType enum value.",
        )

    # Initialize available frameworks if needed
    if _AVAILABLE_FRAMEWORKS is None:
        _AVAILABLE_FRAMEWORKS = _get_available_frameworks()

    # Check if framework is implemented
    if framework not in _AVAILABLE_FRAMEWORKS:
        # Check if framework exists in FrameworkType enum but is not implemented
        all_framework_types = [ft for ft in FrameworkType]
        if framework in all_framework_types:
            implemented_frameworks = [
                ft.name for ft in _AVAILABLE_FRAMEWORKS.keys()
            ]
            raise NotImplementedError(
                f"Framework '{framework.name}' is not implemented yet. "
                f"Available frameworks: {implemented_frameworks}",
            )
        else:
            # This should not happen if framework is a valid FrameworkType, but just in case
            raise ValueError(f"Unknown framework type: {framework}")

    return _AVAILABLE_FRAMEWORKS[framework]


def get_supported_frameworks():
    """
    Get a list of all currently supported (implemented) framework types.
    """
    global _AVAILABLE_FRAMEWORKS

    if _AVAILABLE_FRAMEWORKS is None:
        _AVAILABLE_FRAMEWORKS = _get_available_frameworks()

    return list(_AVAILABLE_FRAMEWORKS.keys())
