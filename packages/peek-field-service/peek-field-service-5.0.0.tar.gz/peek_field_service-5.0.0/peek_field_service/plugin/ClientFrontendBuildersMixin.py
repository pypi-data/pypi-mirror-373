import logging

import os

from peek_plugin_base.util.build_doc.DocBuilder import DocBuilder
from peek_plugin_base.util.build_frontend.WebBuilder import WebBuilder

logger = logging.getLogger(__name__)


class ClientFrontendBuildersMixin:
    def _buildWebApp(self, loadedPlugins):
        # --------------------
        # Prepare the Peek Mobile

        from peek_platform import PeekPlatformConfig

        try:
            import peek_field_app

            mobileProjectDir = os.path.dirname(peek_field_app.__file__)

        except:
            logger.warning(
                "Skipping builds of peek-field-app"
                ", the package can not be imported"
            )
            return

        fieldWebBuilder = WebBuilder(
            mobileProjectDir,
            "peek-field-app",
            PeekPlatformConfig.config,
            loadedPlugins,
        )
        yield fieldWebBuilder.build()

    def _buildDocs(self, loadedPlugins):
        # --------------------
        # Prepare the User Docs
        from peek_platform import PeekPlatformConfig

        try:
            import peek_field_doc

            docProjectDir = os.path.dirname(peek_field_doc.__file__)

        except:
            logger.warning(
                "Skipping builds of peek_field_doc"
                ", the package can not be imported"
            )
            return

        docBuilder = DocBuilder(
            docProjectDir,
            "peek-field-doc",
            PeekPlatformConfig.config,
            loadedPlugins,
        )
        yield docBuilder.build()
