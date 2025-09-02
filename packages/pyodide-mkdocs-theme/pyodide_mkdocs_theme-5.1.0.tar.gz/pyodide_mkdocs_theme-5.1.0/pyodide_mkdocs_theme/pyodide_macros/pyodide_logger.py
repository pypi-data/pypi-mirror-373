"""
pyodide-mkdocs-theme
Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

# Logger object to use to "hook" into mkdocs' logger: all the messages of this logger will
# appear during `mkdocs serve`.
#
# To use it:
#
# * import the logger object in the file where you need it
# * log messages with various levels of logging:
#     - logger.error(msg)
#     - logger.warn(msg)
#     - logger.info(msg)
#     - logger.debug(msg)
#
# ---
#
# See: https://github.com/mkdocs/mkdocs/discussions/3241


import logging
import platform
from typing import Any, MutableMapping, Tuple








class Logger(logging.LoggerAdapter):
    """A logger adapter to prefix messages with the originating package name."""


    def __init__(self, prefix: str, logger_: logging.Logger, color:int=None):
        """Initialize the object.

        Arguments:
            prefix: The string to insert in front of every message.
            logger: The logger instance.
        """
        super().__init__(logger_, {})
        self.prefix = prefix
        if platform.system() != 'Windows':
            color = 36 if color is None else color
            self.prefix = f"\033[{ color }m{ prefix }\033[0m"


    def process(self, msg: str, kwargs: MutableMapping[str, Any]) -> Tuple[str, Any]:
        """Process the message.

        Arguments:
            msg: The message:
            kwargs: Remaining arguments.

        Returns:
            The processed message.
        """
        return f"{self.prefix}: {msg}", kwargs



def get_plugin_logger(name: str, color:int=None) -> Logger:
    """Return a logger for plugins.

    Arguments:
        name: The name to use with `logging.getLogger`.

    Returns:
        A logger configured to work well in MkDocs,
            prefixing each message with the plugin package name.
    """
    _logger = logging.getLogger(f"mkdocs.macros.{name}")
    return Logger(name.split(".", 1)[0], _logger, color)




# sub-logger for pyodide-mkdocs-theme:
logger = get_plugin_logger(__name__.replace('_','-'))
