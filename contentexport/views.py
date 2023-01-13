# -*- coding: UTF-8 -*-
from contentexport.interfaces import IContentexportLayer
from plone import api
from Products.Five import BrowserView
from zope.interface import alsoProvides

import logging

logger = logging.getLogger(__name__)

TYPES_TO_EXPORT = []


class ExportAll(BrowserView):

    def __call__(self):
        request = self.request
        if not request.form.get("form.submitted", False):
            return self.index()

        qi = api.portal.get_tool("portal_quickinstaller")
        if not qi.isProductInstalled("contentimport"):
            qi.installProducts(["contentimport"])
            alsoProvides(request, IContentexportLayer)

        portal = api.portal.get()

        export_name = "export_content"
        logger.info("Start {}".format(export_name))
        view = api.content.get_view(export_name, portal, request)
        exported_types = TYPES_TO_EXPORT
        request.form["form.submitted"] = True
        view(portal_type=exported_types, include_blobs=2, download_to_server=True)
        logger.info("Finished {}".format(export_name))

        other_exports = [
            "export_relations",
            "export_members",
            "export_translations",
            "export_localroles",
            "export_ordering",
            "export_defaultpages",
            "export_discussion",
            "export_portlets",
            "export_redirects",
        ]
        for export_name in other_exports:
            export_view = api.content.get_view(export_name, portal, request)
            request.form["form.submitted"] = True
            # store each result in var/instance/export_xxx.json
            export_view(download_to_server=True)

        logger.info("Finished export_all")
        # Important! Redirect to prevent infinite export loop :)
        return self.request.response.redirect(self.context.absolute_url())
