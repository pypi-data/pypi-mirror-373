#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of self software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and self permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
from datetime import datetime
import os
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


try:
    from mss import mss  # @UnresolvedImport
    with_mss = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"MssManager is not available. Initialization failed on error: {exc}")
    with_mss = False

class MssManager(object):
    """ Class managing MSS library.
    
    It is implemented internally with 'mss' package (https://python-mss.readthedocs.io/usage.html)
    """
    
    @classmethod
    def is_available(cls):
        return with_mss
    
    @classmethod
    def make_monitors_screenshots(cls, destination_path, context_description):
        """
        Make screenshots for debug (monitors, current UI in focus).
        @param destination_path Destination path
        @param context_description Context description that will be inserted in file names
        """
        screenshotter = mss()
        
        # Create file prefix
        date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')
        file_prefix = f"{date_str}-{context_description}-monitor"
        screenshot_path = os.path.join(destination_path, file_prefix)
        
        # Take screenshots
        for nb in range(1, len(screenshotter.monitors)):
            screen_path = f"{screenshot_path}{nb}.png"
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Making monitor screenshot of monitor {nb} in '{screen_path}'")
            screenshotter.save(screen_path, nb)
    
    
    
    
    