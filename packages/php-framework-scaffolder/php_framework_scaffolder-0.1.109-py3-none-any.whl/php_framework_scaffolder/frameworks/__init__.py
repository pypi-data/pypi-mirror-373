from __future__ import annotations

from php_framework_scaffolder.frameworks.base import BaseFrameworkSetup
from php_framework_scaffolder.frameworks.cakephp import CakePHPSetup
from php_framework_scaffolder.frameworks.codeigniter import CodeIgniterSetup
from php_framework_scaffolder.frameworks.drupal import DrupalSetup
from php_framework_scaffolder.frameworks.drush import DrushSetup
from php_framework_scaffolder.frameworks.factory import get_framework_handler
from php_framework_scaffolder.frameworks.factory import get_supported_frameworks
from php_framework_scaffolder.frameworks.fastroute import FastRouteSetup
from php_framework_scaffolder.frameworks.fatfree import FatFreeSetup
from php_framework_scaffolder.frameworks.fuel import FuelSetup
from php_framework_scaffolder.frameworks.laminas import LaminasSetup
from php_framework_scaffolder.frameworks.laravel import LaravelSetup
from php_framework_scaffolder.frameworks.na import NaSetup
from php_framework_scaffolder.frameworks.phalcon import PhalconSetup
from php_framework_scaffolder.frameworks.phpixie import PhPixieSetup
from php_framework_scaffolder.frameworks.popphp import PopPHPSetup
from php_framework_scaffolder.frameworks.slim import SlimSetup
from php_framework_scaffolder.frameworks.symfony import SymfonySetup
from php_framework_scaffolder.frameworks.thinkphp import ThinkPHPSetup
from php_framework_scaffolder.frameworks.yii import YiiSetup
from php_framework_scaffolder.frameworks.zendframework import ZendFrameworkSetup


__all__ = [
    'BaseFrameworkSetup',
    'CakePHPSetup',
    'CodeIgniterSetup',
    'DrupalSetup',
    'DrushSetup',
    'FastRouteSetup',
    'FatFreeSetup',
    'FuelSetup',
    'LaminasSetup',
    'LaravelSetup',
    'PhalconSetup',
    'PhPixieSetup',
    'PopPHPSetup',
    'SlimSetup',
    'SymfonySetup',
    'ThinkPHPSetup',
    'YiiSetup',
    'ZendFrameworkSetup',
    'NaSetup',
    'get_framework_handler',
    'get_supported_frameworks',
]
