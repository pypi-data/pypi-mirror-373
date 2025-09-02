#!/usr/bin/env python
"""
 * run_peek_field_service_build_only.py
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  Synerty Pty Ltd
 *
"""

import logging


logger = logging.getLogger(__name__)


from peek_field_service.run_peek_field_service import main as mainMain


def main():
    mainMain(
        loadPlugins=True,
        startPlugins=False,
        serveSite=True,
        serveWebsocket=False,
        siteName="Peek Field Offline Service",
    )


if __name__ == "__main__":
    main()
