import logging

#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################


class Config(object):
    """HolAdo project configuration"""

    # Timeouts
    session_timeout_seconds = 7 * 24 * 3600     # Session timeout is by default to 7 days
    timeout_seconds = 240            # Default timeout
    join_timeout_seconds = 1800      # Long timeout used when a join should stop without deadlock. When this timeout is reached, a TimeoutTechnicalException is raised

    # Message
    message_truncate_length = 500     # Length used to truncate a message when it is too long. When a message is truncated, it is suffixed by '...'

    # Time analysis
    threshold_warn_time_spent_s = 10    # Duration in seconds that triggers a warning on spent time

    # Redo
    redo_wait_process_min_interval_s = 0.001    # In redo, minimal duration to sleep between two verification of process thread end
    redo_wait_process_max_interval_s = 0.1      # In redo, maximal duration to sleep between two verification of process thread end

    # Unique values
    unique_string_padding_length = 6    # Number of characters used to generate a unique text suffix
     
    # Symbols
    DYNAMIC_SYMBOL = u"%"
    THREAD_DYNAMIC_SYMBOL = u"@"
    UNIQUE_SYMBOL = u"#"
    NOT_APPLICABLE_SYMBOL = u"N/A"
    NONE_SYMBOL = u"None"
    
    # Default log levels
    log_level_grpc_request = logging.INFO
    log_level_rest_request = logging.INFO

