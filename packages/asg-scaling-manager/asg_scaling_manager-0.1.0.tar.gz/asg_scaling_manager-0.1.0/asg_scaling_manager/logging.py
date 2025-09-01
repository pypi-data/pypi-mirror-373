import structlog

_logger = None


def get_logger():
    global _logger
    if _logger is None:
        structlog.configure(
            processors=[
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
        )
        _logger = structlog.get_logger("asg-scaling-manager")
    return _logger


