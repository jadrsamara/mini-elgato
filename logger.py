import logging
import traceback
import sys
import newrelic_logger
import os

env = os.environ['APP_TAGS_ENV']
service = os.environ['NEW_RELIC_APP_NAME']

"""
System Logger, mainly for any Uncaught exceptions
"""

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback), extra={
        "env":env,
        "service":service,
    })

sys.excepthook = handle_exception


"""
App Logger, for any logs added in the code
"""

class SystemLogFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'user_id'):
            record.env = env
            record.service = service
        return True

root_logger = logging.getLogger()
root_logger.addFilter(SystemLogFilter())


def info(message, ctx):
    """
    Info logger interface
    """
    logging.info(message, extra={
        "user_name":ctx.message.author,
        "command":ctx.command,
        "server_name":ctx.guild,
        "server_id":ctx.guild.id
    })


def warn(message, ctx):
    """
    Warn logger interface
    """
    logging.warn(message, extra={
        "user_name":ctx.message.author,
        "command":ctx.command,
        "server_name":ctx.guild,
        "server_id":ctx.guild.id
    })


async def error(error, ctx):
    """
    Error logger interface
    """
    logging.error(error, extra={
        "traceback":"".join(traceback.format_exception(type(error), error, error.__traceback__)),
        "user_name":ctx.message.author,
        "command":ctx.command,
        "server_name":ctx.guild,
        "server_id":ctx.guild.id
    })

    await ctx.send(content=error,ephemeral=True)

