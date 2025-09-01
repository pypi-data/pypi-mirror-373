# ========================================================================================
#  Copyright (C) 2025 CryptoLab Inc. All rights reserved.
#
#  This software is proprietary and confidential.
#  Unauthorized use, modification, reproduction, or redistribution is strictly prohibited.
#
#  Commercial use is permitted only under a separate, signed agreement with CryptoLab Inc.
#
#  For licensing inquiries or permission requests, please contact: pypi@cryptolab.co.kr
# ========================================================================================

import os
import sys

from loguru import logger

# Configure logger based on environment variable
log_level = os.getenv("ES2_LOG_LEVEL", "").upper()
if log_level in ["DEBUG", "INFO", "ERROR"]:
    logger.add(sys.stdout, format="{time:YY-MM-DD at HH:mm:ss} | {level} | {message}", level=log_level)
else:
    logger.disable("")

# Export the logger for use in other modules
__all__ = ["logger"]
