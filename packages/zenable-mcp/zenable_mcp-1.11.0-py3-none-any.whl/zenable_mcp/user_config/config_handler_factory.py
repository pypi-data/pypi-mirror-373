from zenable_mcp.user_config.config_handler import FileConfigHandler
from zenable_mcp.user_config.config_parser import (
    UserTomlConfigParser,
    UserYamlConfigParser,
)
from zenable_mcp.user_config.local_file_provider import LocalFileProvider


def get_local_config_handler():
    """
    Factory function to create the default local config handler.
    """

    config_file_name = "zenable_config"

    file_provider = LocalFileProvider()
    config_parsers = [UserTomlConfigParser(), UserYamlConfigParser()]
    config_handler = FileConfigHandler(file_provider, config_parsers, config_file_name)

    return config_handler
