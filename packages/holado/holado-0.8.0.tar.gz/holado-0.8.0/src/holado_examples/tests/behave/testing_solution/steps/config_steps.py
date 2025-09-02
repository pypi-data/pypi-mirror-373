# -*- coding: utf-8 -*-

import logging
from holado_test.behave.behave import *  # @UnusedWildImport
from holado.common.context.session_context import SessionContext
from config.config_manager import TSConfigManager


logger = logging.getLogger(__name__)


def __get_config_manager() -> TSConfigManager:
    return SessionContext.instance().config_manager


@Given(r"ensure system is configured with default settings")
def step_impl(context):
    __get_config_manager().configure_system_with_default_settings()



