# -*- coding: utf-8 -*-

from .vendor.vislog import VisLog

logger = VisLog(
    name="pyproject_ops",
    log_format="%(message)s",
)
