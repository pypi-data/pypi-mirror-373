"""Init and utils."""

from zope.i18nmessageid import MessageFactory

import logging


__version__ = "1.0.0a19"

PACKAGE_NAME = "kitconcept.core"
DEFAULT_PROFILE = f"{PACKAGE_NAME}:base"
CMF_DEPENDENCIES_PROFILE = f"{PACKAGE_NAME}:cmfdependencies"
DEPENDENCIES_PROFILE = f"{PACKAGE_NAME}:dependencies"

_ = MessageFactory(PACKAGE_NAME)

logger = logging.getLogger(PACKAGE_NAME)


def initialize(context):
    from kitconcept.core.tools import migration
    from Products.CMFPlone.utils import ToolInit

    tools = (migration.MigrationTool,)
    # Register tools and content
    ToolInit(
        "Plone Tool",
        tools=tools,
        icon="tool.gif",
    ).initialize(context)
