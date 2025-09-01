from kitconcept.core import logger
from Products.GenericSetup.tool import SetupTool


def null_upgrade_step(tool: SetupTool):
    """This is a null upgrade, use it when nothing happens"""
    logger.info("Null migration step.")
    pass
