import yaml
import logging
import logging.config
from pathlib import Path

from .saving import log_path


LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s %(name)s[%(process)d] %(levelname)-8s[%(module)s:%(lineno)d] %(message)s'


def setup_logging(run_config, log_config="logging.yml") -> None:
    """
    Setup ``logging.config``

    Parameters
    ----------
    run_config : str
        Path to configuration file for run

    log_config : str
        Path to configuration file for logging
    """
    log_config = Path(log_config)

    if not log_config.exists():
        logging.basicConfig(level=LOG_LEVEL)
        logger = logging.getLogger("setup")
        logger.warning(f'"{log_config}" not found. Using basicConfig.')
        return

    with open(log_config, "rt") as f:
        config = yaml.safe_load(f.read())

    # modify logging paths based on run config
    run_path = log_path(run_config)
    for _, handler in config["handlers"].items():
        if "filename" in handler:
            handler["filename"] = str(run_path / handler["filename"])

    logging.config.dictConfig(config)
    setup_logger(reconfigure=True)


def setup_logger(name=None, log_level=LOG_LEVEL, **kw):
    if name is not None:
        log = logging.getLogger()
    else:
        log = logging.getLogger(f'pytorch_conv_lstm.{name}')
    log.setLevel(log_level)
    try:
        import coloredlogs
    except ModuleNotFoundError:
        log.debug('coloredlogs not installed -- falling back to standard logging.')
    else:
        log_fmt = kw.pop('fmt', LOG_FORMAT)
        coloredlogs.install(logger=log, level=log_level, fmt=log_fmt, **kw)
    return log
